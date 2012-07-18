import mock

import nap
from . import SampleRemoteModel


expected_note_output = {
    "content": "hello",
    "id": "75",
    "resource_uri": "/api/v1/note/75/",
    "title": "a title",
    "some_field": "some field",
    "when": "2012-07-08T22:02:49.712163"
}


class TestManagerMethods(object):

    def test_get(self):
        api = nap.API('http://slumber.in/api/v1/', auth=('demo', 'demo'))
        with mock.patch('slumber.Resource.post') as slumber_post:
            slumber_post.return_value = expected_note_output
            note_dict = api.note.post({'title': 'a title', 'content': 'hello'})
        note_id = note_dict['id']
        api.register_resource(SampleRemoteModel, 'note')
        with mock.patch('slumber.Resource.get') as slumber_get:
            slumber_get.return_value = expected_note_output
            note = api.note(note_id).get()

        assert note.title == 'a title'
        assert note.content == 'hello'
        assert note.extra_data['id'] == u'75'
