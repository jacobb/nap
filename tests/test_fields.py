import datetime
import pytest

from . import AuthorModel
from nap.fields import (Field, ResourceField, ListField,
        DictField, DateTimeField)


class TestFields(object):

    def test_field(self):

        field = Field(default='xyz')

        assert field.get_default() == 'xyz'
        assert field.scrub_value('123') == '123'

    def test_readonly(self):

        field = Field()
        assert field.readonly == False

        readonly_field = Field(readonly=True)
        assert readonly_field.readonly == True

        pk_field = Field(resource_id=True)
        assert pk_field.readonly == True

        pk_readonly_field = Field(resource_id=True, readonly=False)
        assert pk_readonly_field.readonly == False

    def test_resource_field(self):
        field = ResourceField(AuthorModel)
        author_dict = {
            'name': 'Jacob',
            'email': 'elitist@gmail.com',
        }
        resource = field.scrub_value(author_dict)

        assert resource.name == 'Jacob'
        assert resource.email == 'elitist@gmail.com'
        new_author_dict = field.descrub_value(resource)

        assert new_author_dict == author_dict

    def test_list_field(self):
        field = ListField(AuthorModel)
        author_dict_list = [
            {
                'name': 'Jacob',
                'email': 'elitist@gmail.com',
            },
            {
                'name': "Bob",
                'email': None
            },
            {
                'name': "Jane",
                "email": "jane@doe.com",
            }
        ]
        resource_list = field.scrub_value(author_dict_list)

        assert len(resource_list) == 3
        assert resource_list[0].name == 'Jacob'
        assert resource_list[1].name == 'Bob'
        assert resource_list[2].name == 'Jane'

        assert resource_list[0].email == 'elitist@gmail.com'
        assert resource_list[1].email == None
        assert resource_list[2].email == 'jane@doe.com'

        new_author_dict_list = field.descrub_value(resource_list)

        assert new_author_dict_list == author_dict_list

    def test_empty_list_field(self):
        field = ListField(AuthorModel)
        assert field.scrub_value([]) == []
        assert field.scrub_value(None) == []

    def test_empty_dict_field(self):
        field = DictField(AuthorModel)
        assert field.scrub_value({}) == {}
        assert field.scrub_value(None) == {}

    def test_dict_field(self):
        field = DictField(AuthorModel)
        author_dict_dict = {
            'main': {
                'name': 'Jacob',
                'email': 'elitist@gmail.com',
            },
            'ghost_writer': {
                'name': "Bob",
                'email': None,
            },
        }
        resource_dict = field.scrub_value(author_dict_dict)

        assert len(resource_dict.keys()) == 2
        assert resource_dict['main'].name == 'Jacob'
        assert resource_dict['main'].email == 'elitist@gmail.com'

        assert resource_dict['ghost_writer'].name == 'Bob'

        new_author_dict_dict = field.descrub_value(resource_dict)
        assert new_author_dict_dict == author_dict_dict

    def test_datetime_field(self):

        field = DateTimeField()

        dt_str = '2012-08-21T22:30:14'
        expected_dt = datetime.datetime(year=2012, month=8, day=21,
                                        hour=22, minute=30, second=14)
        assert field.scrub_value(dt_str) == expected_dt
        assert field.descrub_value(expected_dt) == dt_str

        # make sure microseconds is stripped
        micro_dt_str = '2012-08-21T22:30:14.24234234'
        assert field.scrub_value(micro_dt_str) == expected_dt
        assert field.descrub_value(expected_dt) == dt_str

    def test_empty_datetime_field(self):

        field = DateTimeField()
        assert field.scrub_value(None) == None

    def test_datetime_field_new_dt_format(self):

        boring_format = "%Y-%m-%d %H:%M:%S"
        field = DateTimeField(dt_format=boring_format)

        dt_str = '2010-06-02 16:30:06'
        expected_dt = datetime.datetime(year=2010, month=6, day=2,
                                        hour=16, minute=30, second=6)
        assert field.scrub_value(dt_str) == expected_dt
        assert field.descrub_value(expected_dt) == dt_str

        field = DateTimeField(dt_formats=(boring_format, "%Y-%m-%dT%H:%M:%S"))
        dt_str2 = '2010-06-02T16:30:06'
        bad_string = "2010/06/02 16:30 06 seconds"
        expected_dt = datetime.datetime(year=2010, month=6, day=2,
                                        hour=16, minute=30, second=6)
        assert field.scrub_value(dt_str) == expected_dt
        assert field.scrub_value(dt_str2) == expected_dt
        assert field.descrub_value(expected_dt) == dt_str

        with pytest.raises(ValueError):
            field.scrub_value(bad_string)

        # make sure microseconds is stripped
        micro_dt_str = '2010-06-02 16:30:06.24234234'
        assert field.scrub_value(micro_dt_str) == expected_dt
        assert field.descrub_value(expected_dt) == dt_str
