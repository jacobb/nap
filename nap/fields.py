class Field(object):

    def __init__(self, api_name=None, default=None, resource_id=False, readonly=None):
        self.api_name = api_name
        self.default = default
        self.resource_id = resource_id

        if readonly is None:
            self.readonly = True if resource_id else False
        else:
            self.readonly = readonly

    def get_default(self):
        return self.default

    def scrub_value(self, val):
        return val

    def descrub_value(self, val):
        return val


class ResourceField(Field):

    def __init__(self, resource_model, *args, **kwargs):
        self.resource_model = resource_model
        super(ResourceField, self).__init__(*args, **kwargs)

    def coerce(self, val):

        if isinstance(val, self.resource_model):
            return val

        return self.resource_model(**val)

    def scrub_value(self, val):
        """
        Val should be a string representing a resource_model object
        """

        if not val:
            return None
        resource = self.coerce(val)
        return resource

    def descrub_value(self, val):
        if not val:
            return None
        return val.to_python()


class ListField(ResourceField):

    def scrub_value(self, val):

        resource_list = [self.coerce(v) for v in val]
        return resource_list

    def descrub_value(self, val):
        obj_list = [obj.to_python() for obj in val]
        return obj_list


class DictField(ResourceField):

    def scrub_value(self, val):
        """
        Val should be a string representing a resource_model object
        """

        resource_dict = dict([
            (k, self.coerce(v)) for (k, v) in val.iteritems()
        ])
        return resource_dict

    def descrub_value(self, val):
            """
            Val should be a string representing a resource_model object
            """

            resource_dict = dict([
                (k, v.to_python()) for (k, v) in val.iteritems()
            ])
            return resource_dict
