import json

import requests

from .lookup import LookupURL
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
        model_name = getattr(options, 'name', model_cls.__name__.lower())

        _meta = {
            'name': model_name,
            'root_url': getattr(options, 'root_url', None)
        }

        for name, attr in attrs.iteritems():
            if isinstance(attr, Field):
                attr._name = name
                fields[name] = attr
                setattr(model_cls, name, attr)

        _meta['fields'] = fields
        setattr(model_cls, '_meta', _meta)
        setattr(model_cls, '_lookup_urls', [])
        return model_cls


class RemoteModel(object):

    __metaclass__ = DataModelMetaClass

    def __init__(self, *args, **kwargs):

        class_name = self.__class__.__name__
        model_fields = self._meta['fields']
        self._root_url = kwargs.get('root_url', self._meta['root_url'])
        if not self._root_url:
            raise ValueError("Must declare a root_url in either %s's Meta"
                            " class or as an keyword argument" % class_name)
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

    @classmethod
    def get_lookup_url(cls, **kwargs):
        """
        Cycle through all look up urls.

        If one is a successful match with the given kwargs, return it
        """
        for url in cls._lookup_urls:
            lookup_url = url.match(**kwargs)
            if lookup_url:
                return lookup_url

        raise ValueError("valid URL for lookup variables not found")

    @classmethod
    def lookup(cls, **kwargs):
        uri, params = cls.get_lookup_url(**kwargs)
        return cls.get(uri, params)

    # write methods

    def get_write_url(self):
        """
        For the time being, save urls behave similarlly to the lookup method.

        However, only the first url listed is respected
        """
        obj_full_url = getattr(self, '_full_url', None)

        if self.full_url:
            return self.full_url

        try:
            url = self._lookup_urls[0]
        except IndexError:
            raise ValueError("a lookup_url must be defined for write operations")

        lookup_var_values = dict([
            (var, getattr(self, var))
            for var in url.required_vars
        ])

        if all(*lookup_var_values.values()):
            uri, params = url.match(**lookup_var_values)

        base_url = "%s%s" % (self._root_url, uri)
        full_url = make_url(base_url, params=params)

        return full_url

    def save(self, **kwargs):

        if self.full_url:
            self.update(**kwargs)
        else:
            self.create(**kwargs)

    def update(self, **kwargs):

        r = requests.put(self.get_write_url(), data=self.to_json())
        return r

    def create(self, **kwargs):

        r = requests.post(self.get_write_url(), data=self.to_json())
        return r

    def to_json(self):
        obj_dict = dict([
            (field_name, getattr(self, field_name))
            for field_name in self._meta['fields'].keys()
        ])
        self._meta['fields'].keys()
        return json.dumps(obj_dict)

    # meta methods
    @classmethod
    def add_lookup_url(cls, pattern, params=None):
        lookup_url = LookupURL(pattern, params)
        cls._lookup_urls.append(lookup_url)


class Field(object):

    def __init__(self, api_name=None, default=None):
        self.api_name = api_name
        self.default = default

    def get_default(self):
        return self.default
