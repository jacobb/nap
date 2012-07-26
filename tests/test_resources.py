import json
import unittest

import nap

import mock

from . import SampleResourceModel


class TestResourceModelCreation(object):

    def test_mapping_to_fields(self):

        dm = SampleResourceModel(title='a', content='b')

        assert dm.title == 'a'
        assert dm.content == 'b'
        assert len(dm.extra_data) == 0

    def test_extra_data(self):

        dm = SampleResourceModel(title='a', note='b', z='c')

        assert dm.extra_data['z'] == 'c'
        assert not hasattr(dm, 'z')

    def test_api_name(self):
        dm = SampleResourceModel(title='a', note='b', some_field='c')

        assert dm.alt_name == 'c'

    def test_meta_attached(self):

        class SampleMetaDataModel(nap.ResourceModel):
            class Meta:
                resource_name = 'bob'
                root_url = "http://foo.com/v1/"

        dm = SampleMetaDataModel()

        assert dm._meta['resource_name'] == 'bob'
        assert dm._meta['root_url'] == "http://foo.com/v1/"

    def test_override_root_url(self):

        different_url = "http://www.differenturl.com/v1/"
        dm = SampleResourceModel(root_url=different_url)
        assert dm._root_url == different_url


class TestResourceModelAccessMethods(object):

    def test_get(self):

        fake_dict = {
            'title': "A fake title",
            'content': "isnt this neat",
        }
        with mock.patch('requests.get') as get:
            stubbed_response = mock.Mock()
            stubbed_response.content = json.dumps(fake_dict)

            model_root_url = SampleResourceModel._meta['root_url']
            expected_url = "%s%s/" % (model_root_url, 'xyz')
            stubbed_response.url = expected_url

            get.return_value = stubbed_response
            obj = SampleResourceModel.get('xyz')

            assert obj.title == fake_dict['title']
            assert obj.content == fake_dict['content']
            assert obj._root_url == model_root_url
            assert obj._full_url == expected_url

    def test_get_lookup_url(self):
        final_uri = SampleResourceModel.get_lookup_url(hello='1', what='2')
        assert final_uri == "1/2/"

        final_uri_with_params = SampleResourceModel.get_lookup_url(
            hello='1',
            what='2',
            extra_param='3'
        )
        assert final_uri_with_params == '1/2/?extra_param=3'
        # assert params == {'extra_param': '3'}
        SampleResourceModel._lookup_urls = []

    def test_lookup(self):
        with mock.patch('nap.resources.ResourceModel.get') as get:
            SampleResourceModel.lookup(hello='hello_test', what='what_test')
            get.assert_called_with('hello_test/what_test/')

        SampleResourceModel._lookup_urls = []

    def test_lookup_no_valid_urls(self):
        from pytest import raises
        with raises(ValueError):
            SampleResourceModel.get_lookup_url(hello='bad_hello')

        SampleResourceModel._lookup_urls = []


class TestSerialize(object):

    def test_serialize(self):
        dm = SampleResourceModel(title='test title', content='test content')
        json_string = dm.serialize()
        obj_dict = json.loads(json_string)
        assert obj_dict['title'] == 'test title'
        assert obj_dict['content'] == 'test content'
        assert obj_dict['alt_name'] == None


class TestResourceModelWriteMethods(unittest.TestCase):

    headers = {'content-type': 'application/json'}

    def tearDown(self):
        SampleResourceModel._lookup_urls = []

    def dont_test_write_url(self):

        dm = SampleResourceModel(
            title='expected_title',
            content='Blank Content')

        url = dm.get_update_url()
        assert url == u'expected_title/'
        SampleResourceModel._lookup_urls = []

    def test_create_url(self):

        class CreateURLModel(nap.ResourceModel):
            class Meta:
                root_url = 'http://www.foo.com/api/'

        cm = CreateURLModel()

        assert cm.get_create_url() == 'createurlmodel/'

        class CreateURLModelTwo(nap.ResourceModel):
            class Meta:
                root_url = 'http://www.foo.com/api/'
                resource_name = 'note'

        cm2 = CreateURLModelTwo()
        assert cm2.get_create_url() == 'note/'

    def test_save(self):
        dm = SampleResourceModel(
            title=None,
            content='Blank Content')
        with mock.patch('nap.resources.ResourceModel.create') as create:
            dm.save()
            assert create.called
        dm._full_url = 'http://www.foo.com/v1/1/'
        with mock.patch('nap.resources.ResourceModel.update') as update:
            dm.save()
            assert update.called

    def test_update(self):
        dm = SampleResourceModel(
            title='expected_title',
            content='Blank Content')
        with mock.patch('requests.put') as put:
            dm.update()
            put.assert_called_with("http://foo.com/v1/expected_title/",
                data=dm.serialize(), headers=self.headers)
        SampleResourceModel._lookup_urls = []

    def test_create(self):

        # add a lookup url to ensure it doesn't get used
        dm = SampleResourceModel(
            title='expected_title',
            content='Blank Content')
        with mock.patch('requests.post') as post:
            dm._full_url = 'http://foo.com/v1/random_title/'
            dm.create()
            post.assert_called_with("http://foo.com/v1/note/",
                data=dm.serialize(), headers=self.headers)
        SampleResourceModel._lookup_urls = []

    def test_write_with_no_lookup_url(self):

        from pytest import raises

        dm = SampleResourceModel(content='what')
        with raises(ValueError):
            dm.update()


class TestResourceID(object):

    def test_resource_id_get(self):
        dm = SampleResourceModel(
            title='expected_title',
            content='Blank Content',
            slug='some-slug')

        assert dm.resource_id == 'some-slug'

    def test_resource_id_set(self):
        dm = SampleResourceModel(
            title='expected_title',
            content='Blank Content',
            slug='some-slug')

        dm.resource_id = 'a-new-slug'

        assert dm.slug == 'a-new-slug'

    def test_resource_id_lookup(self):
        resource_id_url = SampleResourceModel.get_lookup_url(slug='some-slug')

        assert resource_id_url == 'note/some-slug/'
