import mock

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

        mock_request = self.get_fake_request()
        cache_backend = self.get_backend()
        key = cache_backend.get_cache_key(mock_request)
        assert key == 'http://www.foo.com/bar/'

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
