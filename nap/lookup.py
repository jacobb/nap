"""
Classes and functions for url resolving
"""
import sre_parse

from .regex_helper import normalize


class LookupURL(object):

    def __init__(self, pattern, params=None):
        self.pattern = pattern
        if params is None:
            params = []
        self.params = params
        self.url_parts = sre_parse.parse(pattern).pattern.groupdict.keys()

    @property
    def required_vars(self):
        return tuple(self.url_parts + list(self.params))

    def match(self, **kwargs):
        if set(self.required_vars) - set(kwargs.keys()):
            return None

        extra_params = dict([
            item for item in kwargs.items()
            if item[0] not in self.required_vars
        ])
        resource_uri = normalize(self.pattern)[0][0] % kwargs
        return resource_uri, extra_params

    @property
    def is_readonly(self):
        return False
