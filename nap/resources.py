import json

import requests

from .lookup import LookupURL, default_lookup_urls
from .utils import make_url


class DataModelMetaClass(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(DataModelMetaClass, cls).__new__
        parents = [b for b in bases if isinstance(b, DataModelMetaClass)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        model_cls = super_new(cls, name, bases, attrs)
        fields = {}

        options = attrs.pop('Meta', None)
        resource_name = getattr(options, 'resource_name', model_cls.__name__.lower())

        urls = getattr(options, 'urls', default_lookup_urls)
        additional_urls = tuple(getattr(options, 'additional_urls', ()))
        urls += additional_urls

        _meta = {
            'resource_name': resource_name,
            'root_url': getattr(options, 'root_url', None),
            'urls': urls,
        }

        # lookup_urls = getattr(options, 'urls', [])
        for name, attr in attrs.iteritems():
            if isinstance(attr, Field):
                attr._name = name
                fields[name] = attr
                setattr(model_cls, name, attr)

        _meta['fields'] = fields
        setattr(model_cls, '_meta', _meta)
        # setattr(model_cls, '_lookup_urls', lookup_urls)
        return model_cls


class RemoteModel(object):

    __metaclass__ = DataModelMetaClass

    def __init__(self, *args, **kwargs):

        model_fields = self._meta['fields']
        self._root_url = kwargs.get('root_url', self._meta['root_url'])
        field_name_api_name_map = dict([
            (field.api_name or name, name)
            for (name, field) in model_fields.iteritems()
        ])

        extra_data = set(kwargs.keys()) - set(field_name_api_name_map.keys())
        for api_name, field_name in field_name_api_name_map.iteritems():
            if api_name in kwargs:
                value = kwargs[api_name]
            else:
                value = model_fields[field_name].get_default()

            setattr(self, field_name, value)

        self.extra_data = dict([
            (key, kwargs[key])
            for key in extra_data
        ])

    @property
    def full_url(self):
        return getattr(self, '_full_url', None)

    # access methods
    @classmethod
    def get(cls, uri, params=None):

        if not params:
            params = {}

        try:
            root_url = cls._meta['root_url']
        except KeyError:
            raise ValueError("`get` requires root_url to be defined")
        base_url = "%s%s" % (root_url, uri)
        full_url = make_url(base_url, params=params)

        resource_response = requests.get(full_url)
        try:
            resource_data = json.loads(resource_response.content)
        except ValueError:
            raise

        resource_data['root_url'] = root_url
        resource_obj = cls(**resource_data)
        resource_obj._full_url = full_url

        return resource_obj

    def _generate_url(self, url_type='lookup', **kwargs):
        """
        Three set of varaibles to create a full URL

        kwargs
        Current object variables (?)
        meta options
        """

        valid_urls = [
            url for url in self._meta['urls']
            if getattr(url, url_type, False)
        ]
        for url in valid_urls:
            if isinstance(self, RemoteModel):
                base_vars = dict([
                    (var, getattr(self, var))
                    for var in url.required_vars
                    if getattr(self, var, None)
                ])
            else:
                base_vars = {}

            base_vars.update(kwargs)

            model_keywords = {
                'resource_name': self._meta['resource_name']
            }

            base_uri, params = url.match(precompile_vars=model_keywords, **base_vars)

            if base_uri:
                full_uri = make_url(base_uri,
                    params=params)

                return full_uri

        raise ValueError("No valid url")

    @classmethod
    def get_lookup_url(cls, **kwargs):
        """
        Cycle through all look up urls.

        If one is a successful match with the given kwargs, return it
        """
        self = cls()
        return self._generate_url(**kwargs)

        raise ValueError("valid URL for lookup variables not found")

    def get_update_url(self, **kwargs):
        """
        For the time being, save urls behave similarlly to the lookup method.
        """

        if self.full_url:
            return self.full_url

        try:
            update_uri = self._generate_url(**kwargs)
        except ValueError:
            update_uri = None

        return update_uri

    def get_create_url(self):
        return "%s%s/" % (self._root_url, self._meta['resource_name'])

    @classmethod
    def lookup(cls, **kwargs):
        uri = cls.get_lookup_url(**kwargs)
        return cls.get(uri)

    # write methods

    def save(self, **kwargs):

        # this feels off to me, but it should work for now?
        if self.full_url or self.get_update_url():
            self.update(**kwargs)
        else:
            self.create(**kwargs)

    def update(self, **kwargs):

        headers = {'content-type': 'application/json'}

        uri = self.get_update_url()
        if not uri:
            raise ValueError('full_url or non-readonly lookup_urls required for updates')

        url = "%s%s" % (self._root_url, self.get_update_url())

        r = requests.put(url,
            data=self.to_json(),
            headers=headers)

        if r.status_code in (201, 201, 204):
            self._full_url = url

    def create(self, **kwargs):

        headers = {'content-type': 'application/json'}
        requests.post(self.get_create_url(),
            data=self.to_json(),
            headers=headers)

    def to_json(self):
        obj_dict = dict([
            (field_name, getattr(self, field_name))
            for field_name in self._meta['fields'].keys()
        ])
        self._meta['fields'].keys()
        return json.dumps(obj_dict)


class Field(object):

    def __init__(self, api_name=None, default=None, resource_id=False):
        self.api_name = api_name
        self.default = default
        self.resource_id = resource_id

    def get_default(self):
        return self.default
