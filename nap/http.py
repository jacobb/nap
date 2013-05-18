import requests


class NapResponse(object):

    def __init__(self, content, url, status_code=200,
            use_cache=False, headers=None):
        self.status_code = 200
        self.content = content
        self.url = url
        self.use_cache = use_cache
        if not headers:
            headers = {}
        self.headers = headers


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
