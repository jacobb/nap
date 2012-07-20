import json

import nap

import mock

from . import SampleRemoteModel


class TestRemoteModelCreation(object):

    def test_mapping_to_fields(self):

        dm = SampleRemoteModel(title='a', content='b')

        assert dm.title == 'a'
        assert dm.content == 'b'
        assert len(dm.extra_data) == 0

    def test_extra_data(self):

        dm = SampleRemoteModel(title='a', note='b', z='c')

        assert dm.extra_data['z'] == 'c'
        assert not hasattr(dm, 'z')

    def test_api_name(self):
        dm = SampleRemoteModel(title='a', note='b', some_field='c')

        assert dm.alt_name == 'c'

    def test_meta_attached(self):

        class SampleMetaDataModel(nap.RemoteModel):
            class Meta:
                name = 'bob'
                root_url = "http://foo.com/v1/"

        dm = SampleMetaDataModel()

        assert dm._meta['name'] == 'bob'
        assert dm._meta['root_url'] == "http://foo.com/v1/"

    def test_override_root_url(self):

        different_url = "http://www.differenturl.com/v1/"
        dm = SampleRemoteModel(root_url=different_url)
        assert dm._root_url == different_url


class TestRemoteModelAccessMethods(object):

    def test_get(self):

        fake_dict = {
            'title': "A fake title",
            'content': "isnt this neat",
        }
        with mock.patch('requests.get') as get:
            stubbed_response = mock.Mock()
            stubbed_response.content = json.dumps(fake_dict)
            get.return_value = stubbed_response
            obj = SampleRemoteModel.get('xyz')

            model_root_url = SampleRemoteModel._meta['root_url']
            assert obj.title == fake_dict['title']
            assert obj.content == fake_dict['content']
            assert obj._root_url == model_root_url
            assert obj._full_url == "%s%s/" % (model_root_url, 'xyz')

    def test_add_lookup_url(self):
        pattern = r'xx(?P<hello>\d*)(?P<what>.*)'
        SampleRemoteModel.add_lookup_url(pattern)
        SampleRemoteModel._lookup_urls[0].pattern == pattern
        SampleRemoteModel._lookup_urls = []

    def test_get_lookup_url(self):
        pattern = r'(?P<hello>\d*)/(?P<what>.*)/'
        SampleRemoteModel.add_lookup_url(pattern)
        final_url, params = SampleRemoteModel.get_lookup_url(hello='1', what='2')
        assert final_url == "1/2/"

        final_url_with_params, params = SampleRemoteModel.get_lookup_url(
            hello='1',
            what='2',
            extra_param='3'
        )
        assert params == {'extra_param': '3'}
        SampleRemoteModel._lookup_urls = []

    def test_lookup(self):
        pattern = r'(?P<hello>\d*)/(?P<what>.*)/'
        SampleRemoteModel.add_lookup_url(pattern)
        with mock.patch('nap.resources.RemoteModel.get') as get:
            SampleRemoteModel.lookup(hello='hello_test', what='what_test')
            get.assert_called_with('hello_test/what_test/', {})

        SampleRemoteModel._lookup_urls = []

    def test_lookup_no_valid_urls(self):
        from pytest import raises

        pattern = r'(?P<hello>\d*)/(?P<what>.*)/'
        SampleRemoteModel.add_lookup_url(pattern)
        with raises(ValueError):
            SampleRemoteModel.get_lookup_url(hello='bad_hello')

        SampleRemoteModel._lookup_urls = []


class TestToJson(object):

    def test_to_json(self):
        dm = SampleRemoteModel(title='test title', content='test content')
        json_string = dm.to_json()
        obj_dict = json.loads(json_string)
        assert obj_dict['title'] == 'test title'
        assert obj_dict['content'] == 'test content'
        assert obj_dict['alt_name'] == None


class TestRemoteModelWriteMethods(object):

    headers = {'content-type': 'application/json'}

    def test_write_url(self):

        dm = SampleRemoteModel(
            title='expected_title',
            content='Blank Content')

        pattern = r'(?P<title>[^/]+)/'
        dm.add_lookup_url(pattern)

        url = dm.get_write_url()
        assert url == u'http://foo.com/v1/expected_title/'
        SampleRemoteModel._lookup_urls = []

    def test_save(self):
        dm = SampleRemoteModel(
            title='expected_title',
            content='Blank Content')
        with mock.patch('nap.resources.RemoteModel.create') as create:
            dm.save()
            assert create.called
        dm._full_url = 'http://www.foo.com/v1/1/'
        with mock.patch('nap.resources.RemoteModel.update') as update:
            dm.save()
            assert update.called

    def test_update(self):
        SampleRemoteModel.add_lookup_url(r'(?P<title>[^/]+)/')
        dm = SampleRemoteModel(
            title='expected_title',
            content='Blank Content')
        with mock.patch('requests.put') as put:
            dm.update()
            put.assert_called_with("http://foo.com/v1/expected_title/",
                data=dm.to_json(), headers=self.headers)
        SampleRemoteModel._lookup_urls = []

    def test_create(self):

        # add a lookup url to ensure it doesn't get used
        SampleRemoteModel.add_lookup_url(r'(?P<title>[^/]+)/')
        dm = SampleRemoteModel(
            title='expected_title',
            content='Blank Content')
        with mock.patch('requests.post') as post:
            dm._full_url = 'http://foo.com/v1/random_title/'
            dm.create()
            post.assert_called_with("http://foo.com/v1/random_title/",
                data=dm.to_json(), headers=self.headers)
        SampleRemoteModel._lookup_urls = []

    def test_write_with_no_lookup_url(self):

        from pytest import raises

        dm = SampleRemoteModel(title='what')
        with raises(ValueError):
            dm.update()

        with raises(ValueError):
            dm.create()
