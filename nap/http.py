import requests


class NapResponse(object):

    def __init__(self, content, url, status_code,
            use_cache=None, headers=None, request_method=None):
        self.status_code = status_code
        self.content = content
        self.url = url
        self._use_cache = use_cache
        if not headers:
            headers = {}
        self.headers = headers
        self.request_method = request_method

    @property
    def use_cache(self):
        """
        use_cache must be explicitely set to False to bypass the cache.
        This is usually done in the engine classes' get_from_cache method
        """
        return self._use_cache is not False

    @use_cache.setter
    def use_cache(self, val):
        self._use_cache = val


class NapRequest(object):

    """
    A request to send to a nap-modeled API. Primarily used internally within
    ResourceModel methods.
    """

    VALID_HTTP_METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')

    def __init__(self, method, url, data=None, headers=None, auth=None,
            *args, **kwargs):

        self._method = method
        self.url = url
        self.data = data
        if not headers:
            headers = {}
        self.headers = headers
        self.auth = auth
        self.extra_args = args
        self.extra_kwargs = kwargs

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        http_method = value.upper()
        if http_method not in self.VALID_HTTP_METHODS:
            raise ValueError("Invalid method")
        self._method = value

    def send(self):
        response = requests.request(self.method, self.url,
            data=self.data,
            headers=self.headers,
            auth=self.auth,
            *self.extra_args,
            **self.extra_kwargs)

        return response
