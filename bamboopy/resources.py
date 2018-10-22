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


class Directory(Resource):
    """Directory entity resource"""
    def __init__(self, *args, **kwargs):
        super(Directory, self).__init__(*args, **kwargs)

        self.fields = [Field(x) for x in self._raw['fields']]
        self.employees = [Employee(x, self.fields) for x in self._raw['employees']]


class Employee(Resource):
    """Employee entity resource"""
    def __init__(self, raw, fields=[], **kwargs):
        super(Employee, self).__init__(raw, **kwargs)

        self.id = self._raw['id']
        self.fields = {}
        self.categories = None

        for field in fields:
            if isinstance(field, str):
                self.fields[field] = self._raw[field]
            else:
                self.fields[field.id] = prop_type_map.get(field.type, str)(self._raw[field.id])

        if raw.get('category'):
            self.categories = [File(x) for x in raw['category']]

    def __get__(self, instance, owner):
        return functools.partial(self._fields[instance], instance)


class Field(Resource):
    """Field entity resource"""
    def __init__(self, *args, **kwargs):
        super(Field, self).__init__(*args, **kwargs)
        self.id = self._raw['id']
        self.type = self._raw['type']
        self.name = self._raw['name']


class File(Resource):
    """File entity resource"""
    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.id = int(self._raw['id'])
        self.name = self._raw['name']
        self.original_file_name = self._raw['originalFileName']
        self.size = int(self._raw['size'])
        self.date_created = datetime.strptime(self._raw['dateCreated'], '%Y-%m-%d %H:%M:%S')
        self.created_by = self._raw['createdBy']
        self.share_with_employee = self._raw['shareWithEmployee'] == 'yes'


class FilesCategory(Resource):
    """Category entity resource"""
    def __init__(self, *args, **kwargs):
        super(FilesCategory, self).__init__(*args, **kwargs)
        self.id = self._raw['id']
        self.name = self._raw['name']
        self.files = []

        if self._raw.get('file'):
            if isinstance(self._raw['file'], list):
                self.files = [File(x) for x in self._raw['file']]
            else:
                self.files = [File(self._raw['file'])]
