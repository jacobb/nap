import datetime

from .utils import is_string_like


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
        """Turn post-deserialized data into the expected end value
        """
        return val

    def descrub_value(self, val, for_read=False):
        """Turn python data into a serializer-friendly format
        """
        return val


class DateTimeField(Field):

    def __init__(self, *args, **kwargs):
        iso_8601 = "%Y-%m-%dT%H:%M:%S"
        try:
            dt_formats = kwargs.pop('dt_format')
        except KeyError:
            dt_formats = kwargs.pop('dt_formats', (iso_8601,))

        if is_string_like(dt_formats):
            dt_formats = (dt_formats,)

        self.dt_formats = dt_formats
        super(DateTimeField, self).__init__(*args, **kwargs)

    def scrub_value(self, val):

        if not val:
            return None

        if '.' in val:
            val = val.split('.')[0]

        for format in self.dt_formats:
            try:
                scrubbed_val = datetime.datetime.strptime(val, format)
            except ValueError:
                continue
            else:
                break
        else:
            raise ValueError("%s is not a valid time format" % val)
        return scrubbed_val

    def descrub_value(self, val, for_read=False):
        if not val:
            return None
        dt_format = self.dt_formats[0]
        return datetime.datetime.strftime(val, dt_format)


class DateField(Field):

    def __init__(self, *args, **kwargs):
        iso_8601 = "%Y-%m-%d"
        try:
            dt_formats = kwargs.pop('dt_format')
        except KeyError:
            dt_formats = kwargs.pop('dt_formats', (iso_8601,))

        if is_string_like(dt_formats):
            dt_formats = (dt_formats,)

        self.dt_formats = dt_formats
        super(DateField, self).__init__(*args, **kwargs)

    def scrub_value(self, val):

        if not val:
            return None

        for format in self.dt_formats:
            try:
                scrubbed_val = datetime.datetime.strptime(val, format).date()
            except ValueError:
                continue
            else:
                break
        else:
            raise ValueError("%s is not a valid date format" % val)
        return scrubbed_val

    def descrub_value(self, val, for_read=False):
        if not val:
            return None
        dt_format = self.dt_formats[0]
        return datetime.date.strftime(val, dt_format)


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

    def descrub_value(self, val, for_read=False):
        if not val:
            return None
        return val.to_python()


class ListField(ResourceField):

    def scrub_value(self, val):

        if not val:
            return []
        resource_list = [self.coerce(v) for v in val]
        return resource_list

    def descrub_value(self, val, for_read=False):
        if not val:
            return []
        obj_list = [obj.to_python(for_read=for_read) for obj in val]
        return obj_list


class DictField(ResourceField):

    def scrub_value(self, val):
        """
        Val should be a string representing a resource_model object
        """

        if not val:
            return {}

        resource_dict = dict([
            (k, self.coerce(v)) for (k, v) in val.iteritems()
        ])
        return resource_dict

    def descrub_value(self, val, for_read=False):
        """
        Val should be a string representing a resource_model object
        """
        if not val:
            return {}
        resource_dict = dict([
            (k, v.to_python()) for (k, v) in val.iteritems()
        ])
        return resource_dict
