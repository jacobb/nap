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

        #  TODO: should lookup default to False?

        self.url_string = url_string
        if params is None:
            params = []
        self.params = params

        self.lookup = lookup
        self.update = update
        self.create = create
        self.collection = collection

    @property
    def url_vars(self):

        pattern = r'\%\(([\w_\-]+)\)s'
        return re.findall(pattern, self.url_string)

    @property
    def required_vars(self):
        return tuple(self.url_vars + list(self.params))

    def match(self, **lookup_vars):
        if set(self.required_vars) - set(lookup_vars.keys()):
            return None, None

        extra_params = dict([
            item for item in lookup_vars.items()
            if item[0] not in self.required_vars
        ])

        pattern = self.url_string

        resource_uri = pattern % lookup_vars
        return resource_uri, extra_params


def nap_url(*args, **kwargs):
    return LookupURL(*args, **kwargs)

default_lookup_urls = (
    nap_url('%(resource_name)s/', create=True, lookup=False, collection=True),
    nap_url('%(resource_name)s/%(resource_id)s', update=True),
)
