from . import AuthorModel
from nap.fields import Field, ResourceField, ListField, DictField


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
