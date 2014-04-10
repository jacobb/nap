import mock
import pytest
from . import SampleResourceModel

from nap.cache.base import BaseCacheBackend, DEFAULT_TIMEOUT


class TestBaseCacheBackend(object):

    def get_backend(self, **kwargs):
        defaults = {
            'default_timeout': DEFAULT_TIMEOUT,
            'obey_cache_headers': True,
        }
        defaults.update(kwargs)
        return BaseCacheBackend(**defaults)

    def get_fake_request(self, **kwargs):

        defaults = {
            'url': 'http://www.foo.com/bar/',
        }

        defaults.update(kwargs)
        mock_request = mock.Mock()
        for attr, val in defaults.iteritems():
            setattr(mock_request, attr, val)

        return mock_request

    def get_fake_response(self, **kwargs):
        defaults = {
            'status_code': 200,
            'url': 'http://www.foo.com/bar/',
            'headers': {},
        }

        defaults.update(kwargs)
        mock_response = mock.Mock()
        for attr, val in defaults.iteritems():
            setattr(mock_response, attr, val)

        return mock_response

    def test_get_cache_key(self):

        obj = SampleResourceModel(
            title='expected_title',
            content='Blank Content'
        )
        cache_backend = self.get_backend()

        uri = SampleResourceModel.objects.get_lookup_url(resource_obj=obj)
        url = SampleResourceModel.objects.get_full_url(uri)
        key = cache_backend.get_cache_key(SampleResourceModel, url)
        assert key == "note::http://foo.com/v1/expected_title/"

    def test_get_timeout_from_header(self):

        cache_backend = self.get_backend()
        headers = {
            'cache-control': 'public, max-age=2592000'
        }
        mock_response = self.get_fake_response(headers=headers)

        timeout = cache_backend.get_timeout_from_header(mock_response)
        assert timeout == 2592000

    def test_get_timeout(self):
        cache_backend = self.get_backend()
        mock_response = self.get_fake_response()
        timeout = cache_backend.get_timeout(mock_response)
        assert timeout == DEFAULT_TIMEOUT

        cache_backend = self.get_backend(default_timeout=42)
        timeout = cache_backend.get_timeout(mock_response)
        assert timeout == 42

        headers = {
            'cache-control': 'public, max-age=2592000'
        }
        mock_response = self.get_fake_response(headers=headers)
        timeout = cache_backend.get_timeout(mock_response)
        assert timeout == 2592000

        cache_backend = self.get_backend(
            default_timeout=42,
            obey_cache_headers=False
        )
        timeout = cache_backend.get_timeout(mock_response)
        assert timeout == 42


class TestDjangoCacheBackend(TestBaseCacheBackend):

    def get_backend(self, **kwargs):

        django_cache = pytest.importorskip("nap.cache.django_cache")
        defaults = {
            'default_timeout': DEFAULT_TIMEOUT,
            'obey_cache_headers': True,
        }
        defaults.update(kwargs)
        return django_cache.DjangoCacheBackend(**defaults)

    def test_get(self):
        backend = self.get_backend()
        with mock.patch('django.core.cache.cache.get') as dj_cache_get:
            dj_cache_get.return_value = 'a thing'
            res = mock.Mock()
            res.url = 'naprulez.org'
            backend.get(res)
            assert dj_cache_get.called

    def test_set(self):

        backend = self.get_backend()
        with mock.patch('django.core.cache.cache.set') as dj_cache_set:
            res = mock.Mock()
            res.url = 'naprulez.org'
            res.headers = {}

            backend.set(res)
            assert dj_cache_set.called
