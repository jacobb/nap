import mock

import nap


class SampleDataModel(nap.DataModel):
    title = nap.Field()
    content = nap.Field()
    alt_name = nap.Field(api_name='some_field')

    class Meta:
        root_url = "http://foo.com/v1/"

expected_note_output = {
    "content": "hello",
    "id": "75",
    "resource_uri": "/api/v1/note/75/",
    "title": "a title",
    "some_field": "some field",
    "when": "2012-07-08T22:02:49.712163"
}


class TestDataModels(object):

    def test_mapping_to_fields(self):

        dm = SampleDataModel(title='a', content='b')

        assert dm.title == 'a'
        assert dm.content == 'b'
        assert len(dm.extra_data) == 0

    def test_extra_data(self):

        dm = SampleDataModel(title='a', note='b', z='c')

        assert dm.extra_data['z'] == 'c'
        assert not hasattr(dm, 'z')

    def test_api_name(self):
        dm = SampleDataModel(title='a', note='b', some_field='c')

        assert dm.alt_name == 'c'

    def test_meta_attached(self):

        class SampleMetaDataModel(nap.DataModel):
            class Meta:
                name = 'bob'
                root_url = "http://foo.com/v1/"

        dm = SampleMetaDataModel()

        assert dm._meta['name'] == 'bob'
        assert dm._meta['root_url'] == "http://foo.com/v1/"

    def test_override_root_url(self):

        different_url = "http://www.differenturl.com/v1/"
        dm = SampleDataModel(root_url=different_url)
        assert dm._root_url == different_url


class TestManagerMethods(object):

    def test_get(self):
        api = nap.API('http://slumber.in/api/v1/', auth=('demo', 'demo'))
        with mock.patch('slumber.Resource.post') as slumber_post:
            slumber_post.return_value = expected_note_output
            note_dict = api.note.post({'title': 'a title', 'content': 'hello'})
        note_id = note_dict['id']
        api.register_resource(SampleDataModel, 'note')
        with mock.patch('slumber.Resource.get') as slumber_get:
            slumber_get.return_value = expected_note_output
            note = api.note(note_id).get()

        assert note.title == 'a title'
        assert note.content == 'hello'
        assert note.extra_data['id'] == u'75'
