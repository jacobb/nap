import json
import unittest

import pytest
import mock

import nap
from nap.http import NapResponse
from nap.engine import ResourceEngine

from . import SampleResourceModel



class BaseResourceModelTest(object):

    def get_engine(self):
        engine = ResourceEngine(SampleResourceModel)
        return engine


class TestResourceModelURLMethods(BaseResourceModelTest):

    def test_get_lookup_url(self):

        self.engine = self.get_engine()
        final_uri = self.engine.get_lookup_url(hello='1', what='2')
        assert final_uri == "1/2/"

        final_uri_with_params = self.engine.get_lookup_url(
            hello='1',
            what='2',
            extra_param='3'
        )
        assert final_uri_with_params == '1/2/?extra_param=3'
        SampleResourceModel._lookup_urls = []


    def test_delete_url(self):

        self.engine = self.get_engine()
        final_uri = self.engine.get_delete_url(title='1')
        assert final_uri == "1/"


    def test_update_url(self):

        self.engine = self.get_engine()
        final_uri = self.engine.get_delete_url(title='1')
        assert final_uri == "1/"

    def test_create_url(self):

        self.engine = self.get_engine()

        prepend_urls = (nap.lookup.nap_url(r'special_create_url/', create=True, lookup=False),)
        old_urls = self.engine.model._meta['urls']
        new_urls = prepend_urls + old_urls
        self.engine.model._meta['urls'] = new_urls

        final_uri = self.engine.get_create_url()
        assert final_uri == "special_create_url/"

        self.engine.model._meta['urls'] = old_urls


class TestResourceEngineAccessMethods(BaseResourceModelTest):


    def test_get_from_uri(self):

        self.engine = self.get_engine()
        fake_dict = {
            'title': "A fake title",
            'content': "isnt this neat",
        }
        with mock.patch('requests.request') as get:
            stubbed_response = mock.Mock()
            stubbed_response.content = json.dumps(fake_dict)

            model_root_url = self.engine.model._meta['root_url']
            expected_url = "xyz/"
            stubbed_response.url = expected_url
            stubbed_response.status_code = 200

            get.return_value = stubbed_response
            obj = self.engine.get_from_uri('xyz')

            assert obj.title == fake_dict['title']
            assert obj.content == fake_dict['content']
            assert obj._root_url == model_root_url
            assert obj._full_url == expected_url


    def test_request_no_root_url(self):
        engine = self.get_engine()
        root_url = engine.model._meta['root_url']
        del engine.model._meta['root_url']

        with pytest.raises(ValueError):
            engine._request('POST', 'somereallybadurl.com')

        engine.model._meta['root_url'] = root_url

    def test_get(self):

        self.engine = self.get_engine()
        with mock.patch('nap.engine.ResourceEngine.get_from_uri') as g:
            self.engine.get('/some/uri/')
            g.assert_called_once
        with mock.patch('nap.engine.ResourceEngine.lookup') as lookup:
            self.engine.get(pk=1)
            lookup.assert_called_once

    def test_lookup(self):

        self.engine = self.get_engine()
        with mock.patch('nap.engine.ResourceEngine.get_from_uri') as get:
            self.engine.lookup(hello='hello_test', what='what_test')
            get.assert_called_with('hello_test/what_test/')

        SampleResourceModel._lookup_urls = []

    def test_lookup_no_valid_urls(self):

        self.engine = self.get_engine()
        from pytest import raises
        with raises(ValueError):
            self.engine.get_lookup_url(hello='bad_hello')

        SampleResourceModel._lookup_urls = []

    def test_generate_url(self):

        self.engine = self.get_engine()
        rm = self.engine.model(hello='1', slug='slug')
        assert self.engine._generate_url(url_type='create', resource_obj=rm) == 'note/'

        # assert that keyword arguments take precedence over meta arguments
        essay_url = rm.objects._generate_url(url_type='create', resource_name='essay')
        assert essay_url == 'essay/'

        assert rm.objects._generate_url(url_type='update', resource_obj=rm) == 'note/slug/'
        # assert that keyword arguments take predecnce over field values
        new_slug_url = rm.objects._generate_url(url_type='update', slug='new-slug')
        assert new_slug_url == 'note/new-slug/'


class TestResourceCollectionMethods(object):

    def test_collection_field(self):

        SampleResourceModel._meta['collection_field'] = 'objects'
        with mock.patch('requests.request') as request:
            r = mock.Mock()
            collection_dict = {
                'meta': {'something': True},
                'objects': [
                    {'title': 'a'},
                    {'title': 'b', 'content': "b's content"},
                    {'title': 'c'},
                ]
            }
            r.content = json.dumps(collection_dict)
            r.status_code = 200
            request.return_value = r
            objects = SampleResourceModel.objects.all()
            assert request.called
        assert len(objects) == 3
        SampleResourceModel._meta['collection_field'] = None

    def test_filter(self):
        with mock.patch('requests.request') as request:
            r = mock.Mock()
            r.status_code = 200
            r.content = json.dumps([
                {'title': 'hello', 'content': 'content'},
                {'title': 'hello', 'content': 'content'}
            ])
            request.return_value = r
            dms = SampleResourceModel.objects.filter(title='title')

        assert len(dms) == 2


class TestGetResultFromCache(object):

    def test_cached_result(self):

        res_content = 'hello!'
        cached_response = NapResponse(
            content=res_content,
            url='some-url/',
            status_code=200,
        )
        with mock.patch('nap.cache.base.BaseCacheBackend.get') as get:
            get.return_value = cached_response
            res = SampleResourceModel.objects._request('GET', 'some-url/')
            assert res == cached_response

    @mock.patch('nap.cache.base.BaseCacheBackend.get')
    @mock.patch('nap.cache.base.BaseCacheBackend.set')
    def test_cache_set_not_called_on_cached_reselt(self, *mocks):

        get = mocks[1]
        cache_set = mocks[0]

        res_content = json.dumps({'title': 'hello!'})
        cached_response = NapResponse(
            content=res_content,
            url='some-url/',
            status_code=200,
            use_cache=True,
        )
        get.return_value = cached_response
        SampleResourceModel.objects.get_from_uri('some-url/')
        assert not cache_set.called


class TestResourceEngineWriteMethods(unittest.TestCase):

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

    def test_update(self):
        dm = SampleResourceModel(
            title='expected_title',
            content='Blank Content')

        with mock.patch('requests.request') as put:
            r = mock.Mock()
            r.content = ''
            r.status_code = 204
            put.return_value = r
            SampleResourceModel.objects.update(dm)
            data = SampleResourceModel.objects.serialize(dm, for_read=True)
            put.assert_called_with('PUT', "http://foo.com/v1/expected_title/",
                data=data, headers=self.headers, auth=None)
        SampleResourceModel._lookup_urls = []

    def test_create(self):

        # add a lookup url to ensure it doesn't get used
        dm = SampleResourceModel(
            title='expected_title',
            content='Blank Content',
            slug='some_slug')
        with mock.patch('requests.request') as post:
            r = mock.Mock()
            r.content = ''
            r.headers = {'location': 'http://foo.com/v1/random_title/'}
            r.status_code = 201
            post.return_value = r
            SampleResourceModel.objects.create(dm)
            data = SampleResourceModel.objects.serialize(dm, for_read=True)
            post.assert_called_with('POST', "http://foo.com/v1/note/",
                data=data, headers=self.headers, auth=None)
        SampleResourceModel._lookup_urls = []

    def test_write_with_no_lookup_url(self):

        from pytest import raises

        dm = SampleResourceModel(content='what')
        with raises(ValueError):
            SampleResourceModel.objects.update(dm)


def test_modify_request():
    new_headers = {'test-header': '123'}
    default_args = SampleResourceModel._meta['default_request_args']
    default_headers = default_args['headers']

    new_headers.update(default_headers)

    with mock.patch('requests.request') as post:
        r = mock.Mock()
        r.content = '{}'
        r.status_code = 200
        post.return_value = r
        SampleResourceModel.objects.modify_request(headers=new_headers).filter()
        post.assert_called_with(
            'GET', "http://foo.com/v1/note/",
            data=None,
            headers=new_headers,
            auth=None
        )

    SampleResourceModel._lookup_urls = []
