import functools
from datetime import datetime

prop_type_map =  {
    'text': str,
    'integer': int,
    'list': str,  # not sure why documentation says list
}


class Resource(object):
    """Models an entity from BambooHR software"""

    def __init__(self, raw):
        self._raw = raw

    def __getattr__(self, item):
        """Allow access of attributes via names."""
        try:
            return self[item]
        except Exception as exception:
            if item == '__getnewargs__':
                raise KeyError(item)
            if hasattr(self, '_raw') and item in self._raw:
                return self._raw[item]
            else:
                raise AttributeError('{} object has no attribute {} ({})'.format(self.__class__, item, exception))

    def __eq__(self, other):
        """Comparision method."""
        return self.id == other.id

    def __str__(self):
        return str(self._raw)

    def _get(self, key, default=None, type=None):
        if not hasattr(self, '_raw'):
            return

        value = self._raw.get(key, default)
        return type(value) if type else value


class Directory(Resource):
    """Directory entity resource"""
    def __init__(self, *args, **kwargs):
        super(Directory, self).__init__(*args, **kwargs)

        self.fields = [Field(x) for x in self._get('fields')]
        self.employees = [Employee(x, self.fields) for x in self._get('employees')]


class Employee(Resource):
    """Employee entity resource"""
    def __init__(self, raw, fields=None, **kwargs):
        super(Employee, self).__init__(raw, **kwargs)

        self.id = self._get('id', type=float)
        self.fields = {}

        for field in fields:
            if isinstance(field, str):
                self.fields[field] = self._get(field, None)
            else:
                self.fields[field.id] = prop_type_map.get(field.type, str)(self._get(field.id))

        if self._get('category'):
            self.categories = [File(x) for x in self._get('category')]

    def __get__(self, instance, owner):
        return functools.partial(self._fields[instance], instance)


class Field(Resource):
    """Field entity resource"""
    def __init__(self, *args, **kwargs):
        super(Field, self).__init__(*args, **kwargs)
        self.id = self._get('id')
        self.type = self._get('type')
        self.name = self._get('name')


class File(Resource):
    """File entity resource"""
    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.id = self._get('id', type=int)
        self.name = self._get('name')
        self.original_file_name = self._get('originalFileName')
        self.size = self._get('size', type=int)
        self.date_created = datetime.strptime(self._get('dateCreated'), '%Y-%m-%d %H:%M:%S')
        self.created_by = self._get('createdBy')
        self.share_with_employee = self._get('shareWithEmployee') == 'yes'


class FilesCategory(Resource):
    """Category entity resource"""
    def __init__(self, *args, **kwargs):
        super(FilesCategory, self).__init__(*args, **kwargs)
        self.id = self._get('id')
        self.name = self._get('name')
        self.files = []

        if self._get('file'):
            if isinstance(self._get('file'), list):
                self.files = [File(x) for x in self._get('file')]
            else:
                self.files = [File(self._get('file'))]


class Report(Resource):
    """Report entity resource"""
    def __init__(self, *args, **kwargs):
        super(Report, self).__init__(*args, **kwargs)

        self.title = self._get('title')
        self.fields = []
        self.employees = []

        if self._get('fields'):
            self.fields = [Field(x) for x in self._get('fields')]

        if self._get('employees'):
            fieldlist = list(map(lambda x: x.id, self.fields))
            self.employees = [Employee(x, fieldlist) for x in self._get('employees')]


class User(Resource):
    """User entity resource"""
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.id = self._get('id', type=int)
        self.employee_id = self._get('employeeId')
        self.first_name = self._get('firstName')
        self.last_name = self._get('lastName')
        self.email = self._get('email')
        self.status = self._get('status')
        last_login = self._get('lastLogin')
        if last_login:
            self.last_login = datetime.strptime(last_login[0:-6], '%Y-%m-%dT%H:%M:%S')


class TabularField(Resource):
    """Tabular Field entity resource"""
    def __init__(self, *args, **kwargs):
        super(TabularField, self).__init__(*args, **kwargs)
        self.alias = self._get('alias')
        self.fields = []

        if self._get('fields'):
            self.fields = [Field(x) for x in self._get('fields')]
