"""
Classes and functions for url resolving
"""
import sre_parse


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
