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
        for name, value in kwargs.iteritems():
            if name in self.fields:
                setattr(self, name, value)
            else:
                self.extra_data[name] = value


class Field(object):
    pass
