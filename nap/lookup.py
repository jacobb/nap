"""
Classes and functions for url resolving
"""
import sre_parse

from .regex_helper import normalize


class LookupURL(object):

    def __init__(self, pattern, params=None, lookup=True, update=False, create=False, collection=False):
        self.pattern = pattern
        if params is None:
            params = []
        self.params = params

        self.lookup = lookup
        self.update = update
        self.create = create
        self.collection = collection

    @property
    def url_parts(self):
        return sre_parse.parse(self.pattern).pattern.groupdict.keys()

    @property
    def required_vars(self):
        return tuple(self.url_parts + list(self.params))

    def match(self, precompile_vars=None, **kwargs):
        if set(self.required_vars) - set(kwargs.keys()):
            return None, None

        extra_params = dict([
            item for item in kwargs.items()
            if item[0] not in self.required_vars
        ])

        if hasattr(precompile_vars, 'keys'):
            pattern = self.pattern % precompile_vars
        else:
            pattern = self.pattern

        resource_uri = normalize(pattern)[0][0] % kwargs
        return resource_uri, extra_params

    @property
    def is_readonly(self):
        return False


def nap_url(*args, **kwargs):
    return LookupURL(*args, **kwargs)

default_lookup_urls = (
    nap_url(r'%(resource_name)s/', create=True, lookup=False),
    nap_url(r'%(resource_name)s/(?P<resource_id>[^/]+)', update=True),
    # nap_url(r'%{resource_name}s/'),
    # nap_url(r'%{resource_name}s/'),
    # nap_url(r'%{resource_name}s/'),
)
