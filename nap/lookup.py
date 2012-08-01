"""
Classes and functions for url resolving
"""
import re


class LookupURL(object):

    def __init__(self, url_string, params=None,
            lookup=True, update=False, create=False, collection=False):
        """
        Setup necesary URL meta options
        """

        self.url_string = url_string
        if params is None:
            params = []
        self.params = params

        self.lookup = lookup
        self.update = update
        self.create = create
        self.collection = collection

    @property
    def url_parts(self):

        pattern = r'\%\(([\w_\-]+)\)s'
        return re.findall(pattern, self.url_string)

    @property
    def required_vars(self):
        return tuple(self.url_parts + list(self.params))

    def match(self, **kwargs):
        if set(self.required_vars) - set(kwargs.keys()):
            return None, None

        extra_params = dict([
            item for item in kwargs.items()
            if item[0] not in self.required_vars
        ])

        pattern = self.url_string

        resource_uri = pattern % kwargs
        return resource_uri, extra_params


def nap_url(*args, **kwargs):
    return LookupURL(*args, **kwargs)

default_lookup_urls = (
    nap_url('%(resource_name)s/', create=True, lookup=False, collection=True),
    nap_url('%(resource_name)s/%(resource_id)s', update=True),
)
