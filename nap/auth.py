import re

import requests


class BaseAuthorization(object):

    def handle_request(self, url, request_func, *args, **kwargs):
        return url, request_func, args, kwargs

    def handle_response(self, response):
        return response


class HttpAuthorization(BaseAuthorization):

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def handle_request(self, url, request_func, *args, **kwargs):
        kwargs['auth'] = (self.user, self.password)

        return url, request_func, args, kwargs


class FoauthAuthorization(BaseAuthorization):

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def handle_request(self, url, request_func, *args, **kwargs):
        self.orig_url = url
        pattern = r'https?://'
        new_url = "https://foauth.org/%s" % re.sub(pattern, '', url)
        kwargs['auth'] = (self.email, self.password)
        headers = kwargs.pop('headers', {})
        if request_func.func_name == 'patch':
            headers['X-HTTP-Method-Override'] = 'PATCH'
            request_func = requests.post

        kwargs['headers'] = headers

        return new_url, request_func, args, kwargs

    def handle_response(self, response):
        response.url = self.orig_url
        return response
