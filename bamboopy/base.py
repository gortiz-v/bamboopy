import io
import gzip
import json
import time
import base64
import ntpath
import logging
import rfc6266
import mimetypes
import traceback
import xmltodict
from http import client
from urllib import parse

from bamboopy import logging_helper
from bamboopy import BambooError, BambooBadRequest, BambooNotFound, BambooTimeout, BambooLimitExceeded, BambooNoPermissions, BambooUnauthorized, BambooServerError

xmltodict_opts = dict(
    attr_prefix='',
    dict_constructor=dict,
)

digest_map_func = {
    'application/json': json.loads,
    'application/xml': lambda x: xmltodict.parse(x, **xmltodict_opts),
    'text/xml': lambda x: xmltodict.parse(x, **xmltodict_opts),
}


class BaseClient(object):
    """Abstract object for interacting with requests API"""

    sleep_multiplier = 1

    def __init__(self, api_key=None, company=None, timeout=10, **extra_options):
        super(BaseClient, self).__init__()

        self.company = company or extra_options.get('company')
        self.api_key = api_key or extra_options.get('api_key')
        self.log = logging_helper.get_log('bamboopy')

        self.options = {'api_base': 'api.bamboohr.com', 'timeout': timeout}
        self.options.update(extra_options)
        self._prepare_connection_type()

    def _prepare_connection_type(self):
        connection_types = {'http': client.HTTPConnection, 'https': client.HTTPSConnection}
        parts = self.options['api_base'].split('://')
        protocol = (parts[0:-1]+['https'])[0]
        self.options['connection_type'] = connection_types[protocol]
        self.options['protocol'] = protocol
        self.options['api_base'] = parts[-1]

    def _get_path(self, subpath):
        raise Exception("Unimplemented get_path for BaseClient subclass!")

    def _prepare_request_auth(self):
        return base64.b64encode("{}:x".format(self.api_key).encode('utf-8')).decode('utf-8')

    def _prepare_request(self, subpath, params, data, opts, files=None, doseq=False, query=''):
        params = params or {}
        url = opts.get('url') or '/api/gateway.php/{}/{}?{}{}'.format(self.company, self._get_path(subpath), parse.urlencode(params, doseq), query)
        headers = opts.get('headers') or {}
        headers.update({
            'Authorization': 'Basic {}'.format(self._prepare_request_auth()),
            'Accept': opts.get('content_type') or 'application/json',
            'Accept-Encoding': 'gzip',
            'Content-Type': opts.get('content_type') or 'application/json'
        })

        if files:
            if not isinstance(files, dict):
                files = {'file': files}

            content_type, multipart_body = self._multipart_encoder(data, files)
            headers.update({
                'Content-Type': content_type,
            })
            data = multipart_body

        if data and not isinstance(data, str) and headers['Content-Type'] == 'application/json':
            data = json.dumps(data)

        return url, headers, data

    def _create_request(self, conn, method, url, headers, data):
        conn.request(method, url, data, headers)
        params = {'method': method, 'url': url, 'data': data, 'headers': headers, 'host': conn.host, 'timeout': conn.timeout}
        return params

    def _path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def _multipart_encoder(self, params, files):
        """https://gist.github.com/rhoit/9573c40feaeb3cf44b4a8544dc0ae2a1"""
        boundary = '----BambooHR-MultiPart-Mime-Boundary----' # uuid.uuid4().hex
        lines = list()
        for key, val in params.items():
            if val is None:
                continue

            lines.append('--' + boundary)
            lines.append('Content-Disposition: form-data; name="%s"' % key)
            lines.extend(['', val])

        for key, uri in files.items():
            name = self._path_leaf(uri)
            mime = mimetypes.guess_type(uri)[0] or 'application/octet-stream'

            lines.append('--' + boundary)
            lines.append('Content-Disposition: form-data; name="{0}"; filename="{1}"'.format(key, name))
            lines.append('Content-Type: ' + mime)
            lines.append('')
            lines.append(open(uri, 'rb').read())

        lines.append('--%s--' % boundary)

        body = bytes()
        for l in lines:
            if isinstance(l, bytes):
                body += l + b'\r\n'
            else:
                body += bytes(l, encoding='utf8') + b'\r\n'

        header = 'multipart/form-data; boundary=' + boundary
        return header, body

    def _gunzip_body(self, body):
        if isinstance(body, bytes):
            sio = io.BytesIO(body)
        else:
            sio = io.StringIO(body)

        gf = gzip.GzipFile(fileobj=sio, mode="rb")
        return gf.read()

    def _process_body(self, data, gzipped):
        if gzipped:
            return self._gunzip_body(data)
        return data

    def _execute_request_raw(self, conn, request):
        try:
            result = conn.getresponse()
        except:
            raise BambooTimeout(None, request, traceback.format_exc())

        encoding = [i[1] for i in result.getheaders() if i[0].lower() == 'content-encoding']
        result.body = self._process_body(result.read(), len(encoding) and encoding[0] == 'gzip')
        conn.close()

        if result.status in (404, 410):
            raise BambooNotFound(result, request)
        elif result.status == 401:
            raise BambooUnauthorized(result, request)
        elif result.status == 403:
            raise BambooNoPermissions(result, request)
        elif result.status == 429:
            raise BambooLimitExceeded(result, request)
        elif 400 <= result.status < 500 or result.status == 501:
            raise BambooBadRequest(result, request)
        elif result.status >= 500:
            raise BambooServerError(result, request)

        return result

    def _execute_request(self, conn, request):
        result = self._execute_request_raw(conn, request)
        return result.body

    def _prepare_request_retry(self, method, url, headers, data, files):
        pass

    def _digest_binary(self, data, headers):
        header = [i[1] for i in headers if i[0].lower() == 'content-disposition']
        if not len(header):
            return data

        cd = rfc6266.parse_headers(header[0], relaxed=True)
        return {
            'filename': cd.filename_unsafe,
            'disposition': cd.disposition,
            'content': data
        }

    def _digest_result(self, data, status, content_type=None):
        content_type = content_type or 'application/json'
        if ';' in content_type:
            content_type = content_type.split(';').pop(0)

        if not data and 200 <= status < 300:
            return True  # No data to display but was a success
        elif not data:
            return

        if isinstance(data, bytes):
            data = data.decode('utf-8')

        return digest_map_func.get(content_type, lambda x: x)(data)

    def _call_raw(self, subpath, params=None, method='GET', data=None, files=None, doseq=False, query='', retried=False, **options):
        opts = self.options.copy()
        opts.update(options)
        url, headers, data = self._prepare_request(subpath, params, data, opts, files, doseq, query)
        kwargs = {'timeout': opts['timeout']}
        num_retries = opts.get('number_retries', 0)

        if method != 'GET' and not opts.get('retry_on_post'):
            num_retries = 0
        if num_retries > 6:
            num_retries = 6
        emergency_brake = 10
        try_count = 0

        while True:
            emergency_brake -= 1
            # avoid getting burned by any mistakes in While loop logic
            if emergency_brake < 1:
                break
            try:
                try_count += 1
                connection = opts['connection_type'](opts['api_base'], **kwargs)
                request_info = self._create_request(connection, method, url, headers, data)
                result = self._execute_request_raw(connection, request_info)
                break
            except BambooUnauthorized as e:
                self.log.warning("401 Unauthorized response to API request.")
                raise
            except BambooError as e:
                if try_count > num_retries:
                    logging.warning("Too many retries for {}".format(url))
                    raise
                # Don't retry errors from 300 to 499
                if e.result and 300 <= e.result.status < 500:
                    raise

                self._prepare_request_retry(method, url, headers, data)
                self.log.warning("BambooError {} calling {}, retrying".format(e, url))
            # exponential back off - wait 0 seconds, 1 second, 3 seconds, 7 seconds, 15 seconds, etc
            time.sleep((pow(2, try_count - 1) - 1 * self.sleep_multiplier))

        return result

    def _call(self, subpath, params=None, method='GET', data=None, files=None, doseq=False, query='', **options):
        result = self._call_raw(subpath, params=params, method=method, data=data, files=files, doseq=doseq, query=query, retried=False, **options)
        content_type = [i[1] for i in result.getheaders() if i[0].lower() == 'content-type']
        content_disposition = [i[1] for i in result.getheaders() if i[0].lower() == 'content-disposition']
        body = result.body
        if len(content_disposition) and 'attachment' in content_disposition[0]:
            body = self._digest_binary(result.body, result.getheaders())

        return self._digest_result(body, status=result.status, content_type=content_type[0] if len(content_type) else None)
