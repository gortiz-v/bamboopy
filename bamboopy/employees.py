from bamboopy import logging_helper
from bamboopy import BaseClient

from bamboopy.resources import Directory, Employee, FilesCategory

SSD_API_VERSION = 1


class Employees(BaseClient):
    def __init__(self, *args, **kwargs):
        super(Employees, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log('bamboopy.employees')

    def _get_path(self, subpath):
        return "v{}/{}".format(self.options.get('version') or SSD_API_VERSION, subpath)

    def _employee_id(self, value):
        if not isinstance(value, str):
            return str(value)

        return value

    def _save(self, filename, content):
        with open(filename, 'wb') as file:
            file.write(bytearray(content))

    # Reports
    # TODO: Reports needs to be added here

    # Employees

    def add(self, first_name, last_name, field_data=None, **options):
        data = {'firstName': first_name, 'lastName': last_name}
        data.update(field_data)
        return self._call("employees/", method='POST', data=data, **options)

    def get(self, employee_id, fields=[], **options):
        fields = fields or ['firstName', 'lastName']
        return Employee(self._call("employees/%s" % self._employee_id(employee_id), query='fields={}'.format(",".join(fields)), **options), fields)

    def update(self, employee_id, field_data=None, **options):
        field_data = field_data or {}
        return self._call("employees/%s" % self._employee_id(employee_id), data=field_data, method='POST', **options)

    def directory(self):
        result = self._call('employees/directory')
        if not result:
            return

        return Directory(result)

    # Employee Files

    def files_list(self, employee_id, **options):
        """List employee files and categories"""
        result = self._call("employees/{}/files/view/".format(self._employee_id(employee_id)), **options)
        if not result:
            return

        categories = result['employee']['category']
        if not isinstance(result['employee']['category'], list):
            categories = [categories]

        return [FilesCategory(x) for x in categories]

    # FIXME: This seems to lack information at the API Documentation
    def add_file_category(self):
        raise NotImplementedError('')

    def update_file(self, employee_id, file_id, filename=None, category_id=None, share=None, **options):
        """Update an employee file"""
        data = {}
        if category_id:
            data.update({'categoryId': category_id})
        if filename:
            data.update({'name': filename})
        if share:
            data.update({'shareWithEmployee': 'yes' if share else 'no'})

        return self._call("employees/{0}/files/{1}".format(self._employee_id(employee_id), file_id), method='POST', data=data, **options)

    def delete_file(self, employee_id, file_id, **options):
        """Delete an employee file"""
        return self._call("employees/{0}/files/{1}/".format(self._employee_id(employee_id), file_id), method='DELETE', **options)

    def download_file(self, employee_id, file_id, dest, **options):
        """Download an employee file"""
        response = self._call("employees/{0}/files/{1}/".format(self._employee_id(employee_id), file_id), **options)
        if not dest or 'content' not in response:
            return response

        filename = self._path_leaf(dest)
        if (filename == '' or filename == '.') and response.get('filename'):
            filename = response['filename']

        self._save(filename, response.pop('content'))
        return response

    def upload_file(self, employee_id, category, file, filename=None, share=False, **options):
        """Upload an employee file"""
        if not filename:
            filename = self._path_leaf(file)
        data = {'category': category, 'fileName': filename, 'share': 'yes' if share else 'no'}
        return self._call("employees/%s/files/" % self._employee_id(employee_id), method='POST', data=data, files=file, **options)
