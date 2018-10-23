from bamboopy import logging_helper
from bamboopy import BaseClient
from bamboopy.resources import User, TabularField, Field

API_VERSION = 1


class Meta(BaseClient):
    def __init__(self, *args, **kwargs):
        super(Meta, self).__init__(*args, **kwargs)
        self.log = logging_helper.get_log('bamboopy.meta')

    def _get_path(self, subpath):
        return "v{}/{}".format(self.options.get('version') or API_VERSION, subpath)

    def _employee_id(self, value):
        if not isinstance(value, str):
            return str(value)

        return value

    def _save(self, filename, content):
        with open(filename, 'wb') as file:
            file.write(bytearray(content))

    # Meta

    def fields(self, **options):
        """Get a list of fields."""
        result = self._call('meta/fields', **options)
        if not result:
            return

        return [Field(x) for x in result]

    def tables(self, **options):
        """Get a list of tabular fields"""
        result = self._call('meta/tables', **options)
        if not result:
            return

        return [TabularField(x) for x in result]

    def users(self, **options):
        result = self._call('meta/users', **options)
        if not result:
            return

        return [User(x) for x in result.values()]
