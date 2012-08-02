from .fields import Field
from .http import NapRequest
from .lookup import default_lookup_urls
from .serializers import JSONSerializer
from .utils import make_url, handle_slash


class DataModelMetaClass(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(DataModelMetaClass, cls).__new__
        parents = [b for b in bases if isinstance(b, DataModelMetaClass)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        model_cls = super_new(cls, name, bases, attrs)
        fields = {}

        options = attrs.pop('Meta', None)
        default_name = model_cls.__name__.lower()
        resource_name = getattr(options, 'resource_name', default_name)

        urls = getattr(options, 'urls', default_lookup_urls)
        append_urls = tuple(getattr(options, 'append_urls', ()))
        prepend_urls = tuple(getattr(options, 'prepend_urls', ()))

        urls = prepend_urls + urls + append_urls

        _meta = {
            'resource_name': resource_name,
            'root_url': getattr(options, 'root_url', None),
            'urls': urls,
            'resource_id_field_name': None,
            'add_slash': getattr(options, 'add_slash', True),
            'update_from_write': getattr(options, 'update_from_write', True),
            'update_method': getattr(options, 'update_method', 'PUT'),
            'auth': getattr(options, 'auth', ()),
        }

        for name, attr in attrs.iteritems():
            if isinstance(attr, Field):
                attr._name = name
                fields[name] = attr
                setattr(model_cls, name, attr)

                if attr.resource_id:
                    _meta['resource_id_field_name'] = name

        _meta['fields'] = fields
        setattr(model_cls, '_meta', _meta)
        return model_cls


class ResourceModel(object):

    __metaclass__ = DataModelMetaClass

    def __init__(self, *args, **kwargs):
        self._root_url = kwargs.get('root_url', self._meta['root_url'])
        self._saved = False
        self.update_fields(kwargs)

    def update_fields(self, field_data):

        self._raw_field_data = field_data
        if not hasattr(field_data, 'keys'):
            """
            field_Data is not a map-like object, so let's try coercing it
            from a string
            """
            serializer = self.get_serializer()
            field_data = serializer.deserialize(field_data)

        model_fields = self._meta['fields']
        api_name_map = dict([
            (field.api_name or name, name)
            for (name, field) in model_fields.iteritems()
        ])

        extra_data = set(field_data.keys()) - set(api_name_map.keys())
        for api_name, field_name in api_name_map.iteritems():
            model_field = model_fields[field_name]

            if api_name in field_data:
                value = model_field.scrub_value(field_data[api_name])
            else:
                value = model_field.get_default()

            setattr(self, field_name, value)

        self.extra_data = dict([
            (key, field_data[key])
            for key in extra_data
        ])

    def _generate_url(self, url_type='lookup', **kwargs):
        valid_urls = [
            url for url in self._meta['urls']
            if getattr(url, url_type, False)
        ]
        for url in valid_urls:
            field_values = dict([
                (var, getattr(self, var))
                for var in url.required_vars
                if getattr(self, var, None)
            ])

            # handle resource_id fields
            if self._resource_id_name in kwargs and 'resource_id' in url.required_vars:
                kwargs['resource_id'] = kwargs[self._resource_id_name]
                if self._resource_id_name not in url.required_vars:
                    del kwargs[self._resource_id_name]

            model_keywords = {
                'resource_name': self._meta['resource_name']
            }

            url_match_vars = dict([
                (k, v) for (k, v) in model_keywords.items()
                if k in url.url_vars
            ])

            url_match_vars.update(field_values)
            url_match_vars.update(kwargs)

            base_url, params = url.match(**url_match_vars)

            if base_url:
                full_url = make_url(base_url,
                    params=params,
                    add_slash=self._meta['add_slash'])

                return full_url

        raise ValueError("No valid url")

    def _request(self, request_method, url, *args, **kwargs):
        try:
            root_url = self._meta['root_url']
        except KeyError:
            raise ValueError("Nap requests require root_url to be defined")

        full_url = "%s%s" % (root_url, url)
        request = NapRequest(request_method, full_url, *args, **kwargs)

        for auth in self._meta['auth']:
            request = auth.handle_request(request)

        print request.url

        resource_response = request.send()

        return resource_response

    # url methods
    @classmethod
    def get_lookup_url(cls, **kwargs):
        self = cls()
        return self._generate_url(**kwargs)

        raise ValueError("no valid URL for lookup found")

    def get_update_url(self, **kwargs):
        if self.full_url:
            return self.full_url

        try:
            update_url = self._generate_url(url_type='update', **kwargs)
        except ValueError:
            update_url = None

        return update_url

    def get_create_url(self, **kwargs):
        return self._generate_url(url_type='create', **kwargs)

    # access methods
    @classmethod
    def get_from_uri(cls, url, *args, **kwargs):
        self = cls(**kwargs)

        url = handle_slash(url, self._meta['add_slash'])
        resource_response = self._request('GET', url, *args, **kwargs)
        resource_data = self.deserialize(resource_response.content)

        self._raw_response_content = resource_data
        self.update_fields(resource_data)
        self._full_url = url

        return self

    @classmethod
    def get(cls, uri=None, **kwargs):

        if uri:
            return cls.get_from_uri(uri)

        return cls.lookup(**kwargs)

    @classmethod
    def lookup(cls, **kwargs):
        uri = cls.get_lookup_url(**kwargs)
        return cls.get_from_uri(uri)

    # collection access methods
    @classmethod
    def all(cls):
        """
        Accesses the first URL set as a collections URL with no additional
        parameters passed.

        Assumes a JSON array will be returned.
        """
        return cls.filter()

    @classmethod
    def filter(cls, **kwargs):
        """
        Accesses the first URL set as a collections URL with no additional
        parameters passed.

        Assumes a JSON array will be returned.
        """
        tmp_obj = cls()
        url = tmp_obj._generate_url(url_type='collection', **kwargs)
        r = tmp_obj._request('GET', url)

        if r.status_code not in (200,):
            raise ValueError('http error')

        serializer = tmp_obj.get_serializer()
        obj_list = serializer.deserialize(r.content)

        if not hasattr(obj_list, '__iter__'):
            raise ValueError('excpeted array-type response')

        resource_list = [cls(**obj_dict) for obj_dict in obj_list]

        return resource_list

    # write methods
    def update(self, **kwargs):
        headers = {'content-type': 'application/json'}

        url = self.get_update_url()
        if not url:
            raise ValueError('No update url found')

        r = self._request(self._meta['update_method'], url,
            data=self.serialize(write=True),
            headers=headers)

        if r.status_code in (200, 201, 204):
            self._full_url = url

        self.handle_update_response(r)

    def handle_update_response(self, r):
        if not self._meta['update_from_write'] or not r.content:
            return

        try:
            self.update_fields(r.content)
        except ValueError:
            return

    def create(self, **kwargs):
        headers = {'content-type': 'application/json'}

        r = self._request('POST', self.get_create_url(),
            data=self.serialize(),
            headers=headers)

        if r.status_code == 201:
            full_url = r.headers.get('location', None)
            self._full_url = full_url.replace(self._root_url, '')

        self.handle_create_response(r)

    def handle_create_response(self, r):

        if not self._meta['update_from_write'] or not r.content:
            return
        try:
            self.update_fields(r.content)
        except ValueError:
            return

    def save(self, **kwargs):
        # this feels off to me, but it should work for now?
        if self._saved or self.full_url or self.get_update_url():
            self.update(**kwargs)
        else:
            self.create(**kwargs)

    # utility methods
    def to_python(self):
        obj_dict = dict([
            (field_name, field.descrub_value(getattr(self, field_name)))
            for field_name, field in self._meta['fields'].iteritems()
            if field.readonly is False
        ])

        return obj_dict

    def serialize(self, write=False):
        serializer = self.get_serializer()
        return serializer.serialize(self.to_python())

    def deserialize(self, val_str):
        serializer = self.get_serializer()
        obj_dict = serializer.deserialize(val_str)

        return obj_dict

    def get_serializer(self):
        return JSONSerializer()

    # properties
    @property
    def full_url(self):
        return getattr(self, '_full_url', None)

    @property
    def _resource_id_name(self):
        if not self._meta['resource_id_field_name']:
            return None
        id_field_name = self._meta['resource_id_field_name']
        return id_field_name

    @property
    def resource_id(self):
        if not self._resource_id_name:
            return None

        return getattr(self, self._resource_id_name)

    @resource_id.setter
    def resource_id(self, resource_id_value):
        if not self._resource_id_name:
            return None
        setattr(self, self._resource_id_name, resource_id_value)

    # etc
    def __unicode__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.resource_id)

    def __repr__(self):
        return unicode(self)
