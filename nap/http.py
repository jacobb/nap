import requests


class NapRequest(object):

    VALID_HTTP_METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')

    def __init__(self, method, url, *args, **kwargs):

        self._method = method
        self.url = url
        self.data = kwargs.pop('data', None)
        self.headers = kwargs.pop('headers', {})
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

    def request(self):
        response = requests.request(self.method, self.url,
            data=self.data,
            headers=self.headers,
            *self.extra_args,
            **self.extra_kwargs
        )
        return response
