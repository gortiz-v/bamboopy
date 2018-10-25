from bamboopy import logging_helper
from bamboopy import BaseClient
from bamboopy.resources import Directory
from bamboopy.resources import Employee
from bamboopy.resources import Field
from bamboopy.resources import FilesCategory
from bamboopy.resources import Report
from bamboopy.resources import TabularField
from bamboopy.resources import User


API_VERSION = 1


class BambooHR(BaseClient):
    def __init__(self, *args, **kwargs):
        super(BambooHR, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log('bamboohr')

    def _get_path(self, subpath):
        return "v{}/{}".format(self.options.get('version') or API_VERSION, subpath)

    def _save(self, filename, content):
        with open(filename, 'wb') as file:
            file.write(bytearray(content))

    def login(self, application_key, email, password):
        """
        Use the Login API to get a key for use in later API requests. Also use the
        response to set up the authentication for future requests. Using this API
        requires you to contact BambooHR to get an applicationKey.
        :param application_key: To ask about an applicationKey, email api@bamboohr.com
        :type application_key: str
        :param email: An email for a user in the account
        :type email: str
        :param password: the password
        :type password: str
        :return:
        """
        pass

    def get_employee(self, employee_id, fields=None, **options):
        """

        :param employee_id: The employee id
        :type employee_id: int
        :param fields: an list of field aliases or ids
        :type fields: list
        :param options:
        :return:
        """
        fields = fields or ['firstName', 'lastName']
        result = self._call("employees/%s" % employee_id, query='fields={}'.format(",".join(fields)), **options)
        if not result:
            return

        return Employee(result, fields)

    def get_report(self, report_id, format, filter_duplicates=True):
        pass

    def update_employee(self, employee_id, field_values=None, **options):
        """
        Update an employee. pass a map of "fieldId" => "value". Does not work for table fields.
        :param employee_id: the employee id
        :type employee_id: int
        :param field_values: the list of field id keys to values
        :type field_values: list
        :param options:
        :return:
        """
        field_values = field_values or {}
        return self._call("employees/%s" % employee_id, data=field_values, method='POST', **options)

    def add_employee(self, first_name, last_name, field_values=None, **options):
        """

        :param first_name: employee first name
        :type first_name: str
        :param last_name: employee last name
        :type last_name: str
        :param field_values: the list of field id keys to values
        :type field_values: list
        :param options:
        :return:
        """
        data = {'firstName': first_name, 'lastName': last_name}
        data.update(field_values)
        return self._call("employees/", method='POST', data=data, **options)

    def get_custom_report(self, format, fields, filter_duplicates=True, title='', last_changed=''):
        """
        :param format: one of xml, csv, xls, json, pdf
        :param fields: a list of field ids or aliases
        :param filter_duplicates: whether to filter duplicate values when employee has multiple rows
        :param title: the title to give the custom report
        :param last_changed: Date in ISO 8601 format, like: 2012-10-17T16:00:00Z
        :return:
        """
        fields = fields or []
        xml = ''
        if title:
            xml += '<title>%s</title>' % title

        if last_changed:
            xml += '<filters><lastChanged includeNull="no">%s</lastChanged></filters>' % last_changed

        if not filter_duplicates:
            xml += '<filterDuplicates>no</filterDuplicates>'

        xml += '<fields>'
        for field in fields:
            xml += '<field id="%s" />' % field
        xml += '</fields>'

        result = self._call("reports/custom/", data='<report>%s</report>' % xml, query="format=%s" % format, method='POST', content_type='text/xml')
        if not result:
            return

        return Report(result)

    def get_table(self, employee_id, table_name='all'):
        """
        :param employee_id: the employee id
        :param table_name: http://www.bamboohr.com/api/documentation/tables.php#tables List of valid tables
        :return:
        """
        return self._call('employees/{0}/tables/{1}/'.format(employee_id, table_name))

    def get_changed_employees(self, since, type='all'):
        pass

    def get_metadata(self, type, **options):
        """

        :param type: a kind of metadata
        :type type: str
        :return:
        """
        return self._call('meta/%s' % type, **options)

    def get_users(self):
        meta = self.get_metadata('users')
        if not meta:
            return

        return [User(x) for x in meta.values()]

    def get_lists(self):
        meta = self.get_metadata('lists')
        if not meta:
            return

        raise NotImplemented("Not yet implemented")

    def get_fields(self):
        meta = self.get_metadata('fields')
        if not meta:
            return

        return [Field(x) for x in meta]

    def get_tables(self):
        meta = self.get_metadata('tables')
        if not meta:
            return

        return [TabularField(x) for x in meta]

    def get_timeoff_balances(self, employee_id, date, precision=1):
        pass

    def get_timeoff_types(self):
        return self.get_metadata('time_off/types')

    def add_table_row(self, employee_id, table_name, values):
        pass

    def add_timeoff_request(self, employee_id, start, end, timeoff_type_id, amount, status, employee_note, manager_note, previous=0):
        pass

    def add_timeoff_history_request(self, employee_id, ymd, request_id):
        pass

    def record_timeoff_override(self, employee_id, ymd, timeoff_type_id, note, amount):
        pass

    def update_table_row(self, employee_id, table_name, row_id, values):
        pass

    def upload_employee_file(self, employee_id, category_id, filename, file, share=False, **options):
        """

        :param employee_id: employee id
        :type employee_id: int
        :param category_id: file category (folder) to add this file to
        :type category_id: int
        :param filename: the name of the file
        :type filename: str
        :param file: the file location
        :type file: str
        :param share: True/False
        :type share: bool
        :param options:
        :return:
        """
        if not filename:
            filename = self._path_leaf(file)
        data = {'category': category_id, 'fileName': filename, 'share': 'yes' if share else 'no'}
        return self._call("employees/%s/files/" % employee_id, method='POST', data=data, files=file, **options)

    def update_timeoff_request_status(self, request_id, status, note):
        pass

    def upload_company_file(self, category_id, filename, file, share=False, **options):
        """

        :param category_id: the category id
        :param filename: the name of the file
        :param file: the path of the file
        :param share: True/False
        :param options:
        :return:
        """
        if not filename:
            filename = self._path_leaf(file)
        data = {'category': category_id, 'fileName': filename, 'share': 'yes' if share else 'no'}
        return self._call("/files/", method='POST', data=data, files=file, **options)

    def list_employee_files(self, employee_id, **options):
        """

        :param employee_id: the employee id
        :type employee_id: int
        :param options:
        :return:
        """
        result = self._call("employees/%s/files/view/" % employee_id, **options)
        if not result:
            return

        categories = result['employee']['category']
        if not isinstance(result['employee']['category'], list):
            categories = [categories]

        return [FilesCategory(x) for x in categories]

    def list_company_files(self, **options):
        """

        :param options:
        :return:
        """
        result = self._call("files/view", **options)
        if not result:
            return

        categories = result['files']['category']
        if not isinstance(result['files']['category'], list):
            categories = [categories]

        return [FilesCategory(x) for x in categories]

    def add_employee_file_category(self, category_name):
        pass

    def add_company_file_category(self, category_name):
        pass

    def update_employee_file(self, employee_id, file_id, filename=None, category_id=None, share=None, **options):
        """

        :param employee_id: the employee id
        :type employee_id: int
        :param file_id: the file id
        :type file_id: int
        :param filename: the name of the file
        :type filename: str
        :param category_id: the category id
        :type category_id: int
        :param share: True/False
        :type share: bool
        :param options:
        :return:
        """
        data = {}
        if category_id:
            data.update({'categoryId': category_id})
        if filename:
            data.update({'name': filename})
        if share:
            data.update({'shareWithEmployee': 'yes' if share else 'no'})

        return self._call("employees/{0}/files/{1}".format(employee_id, file_id), method='POST', data=data, **options)

    def update_company_file(self, file_id, filename=None, category_id=None, share=None, **options):
        """

        :param file_id: the file id
        :type file_id: int
        :param filename: the name of the file
        :type filename: str
        :param category_id: the category id
        :type category_id: int
        :param share: True/False
        :type share: bool
        :param options:
        :return:
        """
        data = {}
        if category_id:
            data.update({'categoryId': category_id})
        if filename:
            data.update({'name': filename})
        if share:
            data.update({'shareWithEmployee': 'yes' if share else 'no'})

        return self._call("/files/%s" % file_id, method='POST', data=data, **options)

    def download_employee_file(self, employee_id, file_id, dest, **options):
        """

        :param employee_id: the employe id
        :param file_id: the file id
        :param dest: destination path
        :param options:
        :return:
        """
        response = self._call("employees/{0}/files/{1}/".format(employee_id, file_id), **options)
        if not dest or 'content' not in response:
            return response

        filename = self._path_leaf(dest)
        if (filename == '' or filename == '.') and response.get('filename'):
            filename = response['filename']

        self._save(filename, response.pop('content'))
        return response

    def download_company_file(self, file_id, dest, **options):
        """

        :param file_id: id of the file
        :type file_id: int
        :param dest: destination path
        :type dest: str
        :param options:
        :return:
        """
        response = self._call("/files/%s/" % file_id, **options)
        if not dest or 'content' not in response:
            return response

        filename = self._path_leaf(dest)
        if (filename == '' or filename == '.') and response.get('filename'):
            filename = response['filename']

        self._save(filename, response.pop('content'))
        return response

    def delete_employee_file(self, employee_id, file_id, **options):
        """

        :param employee_id: the employee id
        :type employee_id: int
        :param file_id: the file id
        :type file_id: int
        :param options:
        :return:
        """
        return self._call("employees/{0}/files/{1}/".format(employee_id, file_id), method='DELETE', **options)

    def delete_company_file(self, file_id, **options):
        """

        :param file_id:
        :param options:
        :return:
        """
        return self._call("/files/%s/" % file_id, method='DELETE', **options)

    def import_employees(self, xml):
        pass

    def get_directory(self):
        result = self._call('employees/directory')
        if not result:
            return

        return Directory(result)

    def download_employee_photo(self, employee_id, size='small', params=None, **options):
        """

        :param employee_id: the employee id
        :type employee_id: int
        :param size: (1|2|small|tiny)
        :type size: str
        :param params: dict(width=100, height=100)
        :type params: dict
        :param options:
        :return:
        """
        return self._call("employees/{0}/photo/{1}".format(employee_id, size), params=params, **options)

    def upload_employee_photo(self, employee_id, file, **options):
        """

        :param employee_id: the employee id
        :type employee_id: int
        :param file: the file location
        :type file: str
        :param options:
        :return:
        """
        return self._call("employees/%s/photo" % employee_id, method='POST', files=file, **options)

    def get_changed_employee_table(self, table_name, since):
        """
        :param table_name:
        :type table_name str
        :param since:
        :type since: datetime
        :return:
        """
        result = self._call('employees/changed/tables/%s' % table_name, query='since=%s' % since)
        if not result:
            return

        return [Field(x) for x in result['employees']]
