class DataModelMetaClass(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(DataModelMetaClass, cls).__new__
        parents = [b for b in bases if isinstance(b, DataModelMetaClass)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        model_cls = super_new(cls, name, bases, attrs)
        fields = {}
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

        self.extra_data = {}
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
