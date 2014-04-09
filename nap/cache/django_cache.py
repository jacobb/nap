try:
    from django.core.cache import cache
except ImportError as e:
    raise ImportError("Error loading django cache module: %s" % e)


from .base import BaseCacheBackend


class DjangoCacheBackend(BaseCacheBackend):

    def get(self, key):
        return cache.get(key)

    def set(self, key, value, response=None):
        timeout = self.get_timeout(response)
        return cache.set(key, value, timeout)
