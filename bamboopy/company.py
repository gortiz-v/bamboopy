from bamboopy import logging_helper
from bamboopy import BaseClient
from bamboopy.resources import FilesCategory

API_VERSION = 1


class Company(BaseClient):
    def __init__(self, *args, **kwargs):
        super(Company, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log('bamboopy.company')

    def _get_path(self, subpath):
        return "v{}/{}".format(self.options.get('version') or API_VERSION, subpath)

    def _save(self, filename, content):
        with open(filename, 'wb') as file:
            file.write(bytearray(content))

    # Company Files

    def files_list(self):
        """List company files and categories"""
        result = self._call("files/view")
        if not result:
            return

        categories = result['files']['category']
        if not isinstance(result['files']['category'], list):
            categories = [categories]

        return [FilesCategory(x) for x in categories]

    # FIXME: This seems to lack information at the API Documentation
    def add_file_category(self):
        """Add a company file category."""
        raise NotImplementedError('')

    def update_file(self, file_id, filename=None, category_id=None, share=None, **options):
        """Update a company file"""
        data = {}
        if category_id:
            data.update({'categoryId': category_id})
        if filename:
            data.update({'name': filename})
        if share:
            data.update({'shareWithEmployee': 'yes' if share else 'no'})

        return self._call("/files/%s" % file_id, method='POST', data=data, **options)

    def delete_file(self, file_id, **options):
        """Delete a company file"""
        return self._call("/files/%s/" % file_id, method='DELETE', **options)

    def download_file(self, file_id, dest, **options):
        """Download a company file"""
        response = self._call("/files/%s/" % file_id, **options)
        if not dest or 'content' not in response:
            return response

        filename = self._path_leaf(dest)
        if (filename == '' or filename == '.') and response.get('filename'):
            filename = response['filename']

        self._save(filename, response.pop('content'))
        return response

    def upload_file(self, category, file, filename=None, share=False, **options):
        """Upload a company file"""
        if not filename:
            filename = self._path_leaf(file)
        data = {'category': category, 'fileName': filename, 'share': 'yes' if share else 'no'}
        return self._call("/files/", method='POST', data=data, files=file, **options)

