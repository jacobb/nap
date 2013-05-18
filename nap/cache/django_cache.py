try:
    from django.core.cache import cache
except ImportError as e:
    raise ImportError("Error loading django cache module: %s" % e)


from .base import BaseCacheBackend


class DjangoCacheBackend(BaseCacheBackend):

    def get(self, response):
        key = self.get_cache_key(response)
        return cache.get(key)

    def set(self, response):
        key = self.get_cache_key(response)
        timeout = self.get_timeout(response)
        return cache.set(key, response, timeout)
