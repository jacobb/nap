import json

import requests

from .lookup import LookupURL
from .utils import make_url
from .regex_helper import normalize


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

        setattr(model_cls, '_meta', _meta)
        for name, attr in attrs.iteritems():
            if isinstance(attr, Field):
                attr._name = name
                fields[name] = attr
                setattr(model_cls, name, attr)

        setattr(model_cls, 'fields', fields)
        setattr(model_cls, '_lookup_urls', [])
        return model_cls


class RemoteModel(object):

    __metaclass__ = DataModelMetaClass

    def __init__(self, *args, **kwargs):

        class_name = self.__class__.__name__
        self.extra_data = {}
        self._root_url = kwargs.get('root_url', self._meta['root_url'])
        if not self._root_url:
            raise ValueError("Must declare a root_url in either %s's Meta"
                            " class or as an keyword argument" % class_name)
        obj_name_api_name_map = dict([
            (field.api_name or name, name)
            for (name, field) in self.fields.iteritems()
        ])
        for name, value in kwargs.iteritems():
            if name in obj_name_api_name_map:
                setattr(self, obj_name_api_name_map[name], value)
            else:
                self.extra_data[name] = value

    @property
    def full_url(self):
        if hasattr(self, '_full_url'):
            return self._full_url

        raise AttributeError("full_url not defined")

    # access methods
    @classmethod
    def get(cls, uri, params=None):

        if not params:
            params = {}

        try:
            root_url = cls._meta['root_url']
        except KeyError:
            raise ValueError("`get` requires root_url to be defined")
        resource_url = "%s%s" % (root_url, uri)

        resource_response = requests.get(resource_url)
        try:
            resource_data = json.loads(resource_response.content)
        except ValueError:
            raise

        resource_data['root_url'] = root_url
        resource_obj = cls(**resource_data)
        resource_obj._full_url = resource_url

        return resource_obj

    @classmethod
    def get_lookup_url(cls, **kwargs):
        for url in cls._lookup_urls:
            if not set(url.required_vars) - set(kwargs.keys()):
                extra_params = dict([
                    item for item in kwargs.items()
                    if item[0] not in url.required_vars
                ])
                resource_uri = normalize(url.pattern)[0][0] % kwargs
                return resource_uri, extra_params

        raise ValueError("valid URL for lookup variables not found")

    @classmethod
    def lookup(cls, **kwargs):
        uri, params = cls.get_lookup_url(**kwargs)
        return cls.get(uri, params)

    # write methods
    def save(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def create(self, *args, **kwargs):
        pass

    # meta methods
    @classmethod
    def add_lookup_url(cls, pattern, params=None):
        lookup_url = LookupURL(pattern, params)
        cls._lookup_urls.append(lookup_url)


class Field(object):

    def __init__(self, api_name=None):
        self.api_name = api_name
