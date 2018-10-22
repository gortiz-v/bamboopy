class EmptyResult(object):
    def __init__(self):
        self.status = 0
        self.body = ''
        self.msg = ''
        self.reason = ''

    def __nonzero__(self):
        return False


class BambooError(ValueError):
    as_str_template = u'''
    ---- request ----
    {method} {host}{url}, [timeout={timeout}]
    ---- body ----
    {body}
    ---- headers ----
    {headers}
    ---- result ----
    {result_status}
    ---- body -----
    {result_body}
    ---- headers -----
    {result_headers}
    ---- reason ----
    {result_reason}
    ---- trigger error ----
    {error}
    '''

    def __init__(self, result, request, err=None):
        super(BambooError, self).__init__(result and result.reason or "Unknown Reason")
        if result is None:
            self.result = EmptyResult()
        else:
            self.result = result
        if request is None:
            request = {}

        self.request = request
        self.err = err

    def __str__(self):
        return self.__unicode__().encode('ascii', 'replace')

    def __unicode__(self):
        params = {}
        request_keys = ('method', 'host', 'url', 'data', 'headers', 'timeout', 'body')
        result_attrs = ('status', 'reason', 'msg', 'body', 'headers')
        params['error'] = self.err

        for key in request_keys:
            params[key] = self.request.get(key)
        for attr in result_attrs:
            params['result_{}'.format(attr)] = getattr(self.result, attr, '')

        params = self._dict_vals_to_unicode(params)
        return self.as_str_template.format(**params)

    def _dict_vals_to_unicode(self, data):
        unicode_data = {}
        for key, val in data.items():
            if not isinstance(val, str):
                unicode_data[key] = str(val, 'utf-8')
            else:
                unicode_data[key] = val
        return unicode_data


class BambooBadRequest(BambooError):
    """Error wrapper for most 40X results"""


class BambooNotFound(BambooError):
    """Error wrapper for 404 results"""


class BambooTimeout(BambooError):
    """Error wrapper for socket timeouts"""


class BambooUnauthorized(BambooError):
    """Error wrapper for unauthorized errors"""


class BambooNoPermissions(BambooError):
    """Error wrapper for lack of permission errors"""


class BambooLimitExceeded(BambooError):
    """Error wrapper for limit exceeds"""


class BambooServerError(BambooError):
    """Error wrapper for most 500 errors"""
