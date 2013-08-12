from .conf import NapConfig
from .fields import Field
from .lookup import default_lookup_urls


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

        meta_conf = {}
        for key in dir(options):
            if not key.startswith('__'):
                meta_conf[key] = getattr(options, key)

        _meta = NapConfig(
            meta_conf,
            resource_name=resource_name,
            urls=urls,
        )

        for name, attr in attrs.iteritems():
            if isinstance(attr, Field):
                attr._name = name
                fields[name] = attr
                setattr(model_cls, name, attr)

                if attr.resource_id:
                    _meta['resource_id_field_name'] = name

        _meta['fields'] = fields
        setattr(model_cls, '_meta', _meta)

        setattr(model_cls, 'objects', _meta['engine_class'](model_cls))
        return model_cls


class ResourceModel(object):

    __metaclass__ = DataModelMetaClass

    def __init__(self, *args, **kwargs):
        """Construct a new model instance
        """
        self._root_url = kwargs.get('root_url', self._meta['root_url'])
        self._request_args = kwargs.pop('request_args', {})

        self._saved = False
        self.update_fields(kwargs)

    def update_fields(self, field_data):
        """Update object's values to values of field_data

        :param field_data: dict-like object with 'Field Name'->'New  Value'
        """

        self._raw_field_data = field_data
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


    def save(self, **kwargs):
        """Contextually save current object. If an object can generate an
        update URL, send an update command. Otherwise, create
        """
        # this feels off to me, but it should work for now?
        update_url = self.objects.get_update_url(self)
        if self._saved or self.full_url or update_url:
            obj = self.objects.update(self, **kwargs)
            self = obj
        else:
            obj = self.objects.create(self, **kwargs)
            self = obj

    # utility methods
    def to_python(self, for_read=False):
        """Converts editable field data to a python dictionary

        :param for_read: include readonly fields.
        """
        obj_dict = dict([
            (field_name, field.descrub_value(getattr(self, field_name)))
            for field_name, field in self._meta['fields'].iteritems()
            if for_read or field.readonly is False
        ])

        return obj_dict

    # properties
    @property
    def full_url(self):
        "Return a pre-set resource URL if available"
        return getattr(self, '_full_url', None)

    @property
    def _resource_id_name(self):
        return self._meta.get('resource_id_field_name', None)

    @property
    def logger(self):
        return self._meta['logger']

    @property
    def resource_id(self):
        "Return object's resource_id value. Returns None if not available"
        if not self._resource_id_name:
            return None
        return getattr(self, self._resource_id_name, None)

    @resource_id.setter
    def resource_id(self, resource_id_value):
        "Set object's resource_id field to ``resource_id_value``"
        if not self._resource_id_name:
            return None
        setattr(self, self._resource_id_name, resource_id_value)

    # etc
    def __unicode__(self):
        return unicode(self.resource_id)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.__unicode__())
