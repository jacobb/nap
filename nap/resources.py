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
        return model_cls


class DataModel(object):

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


class Field(object):

    def __init__(self, api_name=None):
        self.api_name = api_name
