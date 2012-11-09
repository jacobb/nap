import re

DEFAULT_TIMEOUT = 60 * 5


class BaseCacheBackend(object):

    CACHE_EMPTY = "!!!DNE!!!"

    def __init__(self, default_timeout=DEFAULT_TIMEOUT, obey_cache_headers=True):
        self.obey_cache_headers = obey_cache_headers
        self.default_timeout = default_timeout

    def get(self, request):
        return None

    def set(self, request, value):
        return None

    def get_timeout_from_header(self, response):
        cache_headers = response.headers.get('cache-control')
        if cache_headers is None:
            return None

        cache_header_age = re.search(r'max\-?age=(\d+)', cache_headers)
        return int(cache_header_age.group(1))

    def get_cache_key(self, request, **kwargs):

        key_parts = {
            'url': request.url
        }

        cache_key = "%(url)s" % key_parts

        return cache_key

    def get_timeout(self, response):

        if self.obey_cache_headers:
            header_timeout = self.get_timeout_from_header(response)
            if header_timeout:
                return header_timeout

        return self.default_timeout


class CacheRequestsResponse(object):

    def __init__(self, content, status_code=200):
        self.status_code = 200
        self.content = content
