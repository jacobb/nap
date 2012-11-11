try:
    from django.core.cache import cache
except ImportError as e:
    raise ImportError("Error loading django cache module: %s" % e)


from .base import BaseCacheBackend


class DjangoCacheBackend(BaseCacheBackend):

    def get(self, request):
        key = self.get_cache_key(request)
        return cache.get(key)

    def set(self, request, value):
        key = self.get_cache_key(request)
        timeout = self.get_timeout(request)
        return cache.set(key, value, timeout)
