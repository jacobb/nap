from .conf import NapConfig
from .fields import Field
from .http import NapRequest, NapResponse
from .lookup import default_lookup_urls
from .serializers import JSONSerializer
from .utils import make_url, handle_slash

class ListWithAttributes(list):
    def __init__(self, list_vals, extra_data):
        super(ListWithAttributes, self).__init__()
        self.extend(list_vals)
        self.extra_data = extra_data


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

        _meta = NapConfig(
            resource_name=resource_name,
            urls=urls,
        )

        _meta.from_class(options)

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
        """Construct a new model instance
        """
        self._root_url = kwargs.get('root_url', self._meta['root_url'])
        self._saved = False
        self.update_fields(kwargs)

    def update_fields(self, field_data):
        """Update object's values to values of field_data

        :param field_data: dict-like object with 'Field Name'->'New  Value'
        """

        self._raw_field_data = field_data
        if not hasattr(field_data, 'keys'):
            # field_data is not a map-like object, so let's try coercing it
            # from a string
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
        """Iterates through object's URL list to find an approrpiate match
        between ``url_type`` and ``kwargs

        :param url_type: string representing the type of URL to find. options \
        are "lookup", "create", "update" and "collection"
        :param kwargs: additional variables to pass to the LookupURL's match method
        """
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
        "Construct a NapRequest and send it via a requests.rest call"

        try:
            root_url = self._meta['root_url']
        except KeyError:
            raise ValueError("Nap requests require root_url to be defined")

        full_url = "%s%s" % (root_url, url)
        self.logger.info("Trying to hit %s" % full_url)
        request = NapRequest(request_method, full_url, *args, **kwargs)

        for mw in self._meta['middleware']:
            request = mw.handle_request(request)

        # Handle cacheing, unless skipped
        skip_cache = kwargs.get('skip_cache', False)

        use_cache = request_method in self._meta['cached_methods']\
                    and not skip_cache

        if use_cache:
            self.logger.debug("Trying to get cached response for %s" % url)
            cached_response = self.cache.get(request)
            if cached_response:
                self.logger.debug("Got cached response for %s" % url)
                return cached_response

        resource_response = request.send()
        response = NapResponse(
            url=request.url,
            status_code=resource_response.status_code,
            headers=resource_response.headers,
            content=resource_response.content,
            use_cache=use_cache,

        )

        for mw in reversed(self._meta['middleware']):
            response = mw.handle_response(request, response)

        return response

    # url methods
    @classmethod
    def get_lookup_url(cls, **kwargs):
        """Generate a URL suitable for get requests based on ``kwargs``

        :param kwargs: URL lookup variables
        """
        self = cls()
        return self._generate_url(**kwargs)

        raise ValueError("no valid URL for lookup found")

    def get_update_url(self, **kwargs):
        """Generate a URL suitable for update requests based on ``kwargs``

        :param kwargs: URL lookup variables
        """
        if self.full_url:
            return self.full_url

        try:
            update_url = self._generate_url(url_type='update', **kwargs)
        except ValueError:
            update_url = None

        return update_url

    def get_create_url(self, **kwargs):
        """Generate a URL suitable for create requests based on ``kwargs``

        :param kwargs: URL lookup variables
        """
        return self._generate_url(url_type='create', **kwargs)

    def get_delete_url(self, **kwargs):
        """Generate a URL suitable for delete requests based on ``kwargs``

        By default, this is the first valid update URL.

        :param kwargs: URL lookup variables
        """
        return self._generate_url(url_type='update', **kwargs)

    # access methods
    @classmethod
    def get(cls, uri=None, request_kwargs=None, **kwargs):
        """Issues a get request to the API. If ``uri`` is passed, will send a
        request directly to that URL. otherwise, attempt a lookup request.

        :param uri: a string representing an API uri
        :param kwargs: optional variables to send to
            :meth:`~nap.resources.ResourceClass.lookup`
        """

        if uri:
            return cls.get_from_uri(uri, request_kwargs=request_kwargs)

        return cls.lookup(request_kwargs=request_kwargs, **kwargs)

    @classmethod
    def get_from_uri(cls, url, *args, **kwargs):
        """Issues a get request to the API. Request is sent to the model's
        root_url + url keyword argument. \*args and \*\*kwargs are sent to `
        """
        self = cls(**kwargs)
        self.load_from_url(url, *args, **kwargs)

        return self

    @classmethod
    def lookup(cls, request_kwargs=None, **lookup_vars):
        """Creates a get request to the API to the first URL found based on
        ``lookup_vars``

        :param lookup_vars: variables to send to get_lookup_url
        """
        uri = cls.get_lookup_url(**lookup_vars)
        return cls.get_from_uri(uri, request_kwargs=request_kwargs)

    def refresh(self, *args, **kwargs):
        url = self.full_url or self._generate_url(url_type='lookup')
        self.load_from_url(url, *args, **kwargs)

    def load_from_url(self, url, *args, **kwargs):
        """instance method to perform all non-collection get requests
        """
        url = handle_slash(url, self._meta['add_slash'])
        response = self._request('GET', url, *args, **kwargs)

        self.validate_get_response(response)
        self._full_url = url
        self.handle_get_response(response)

    def validate_get_response(self, response):
        """Validate get response is valid to use for updating our object
        """

        self.validate_response(response)
        if response.status_code not in self._meta['valid_get_status']:
            raise ValueError("Expected status code in %s, got %s" %
                (self._meta['valid_get_status'], response.status_code))

    def handle_get_response(self, response):
        """Handle any actions needed after a HTTP Response has ben validated
        for a get (get, refresh, lookup) action
        """
        resource_data = self.deserialize(response.content)

        self._raw_response_content = resource_data
        self.update_fields(resource_data)
        self.handle_response(response)

    # collection access methods
    @classmethod
    def all(cls):
        """Creates a get request to the API to the first collection URL with
        no parameters passed
        """
        return cls.filter()

    @classmethod
    def filter(cls, **lookup_vars):
        """
        Accesses the first URL set as a collections URL with no additional
        parameters passed. Returns a list of current ResourceModel objects

        :param lookup_vars: variables to pass to _generate_url
        """
        tmp_obj = cls()
        url = tmp_obj._generate_url(url_type='collection', **lookup_vars)
        response = tmp_obj._request('GET', url)

        tmp_obj.validate_collection_response(response)

        serializer = tmp_obj.get_serializer()
        r_data = serializer.deserialize(response.content)
        collection_field = cls._meta.get('collection_field')
        if collection_field:
            obj_list = r_data[collection_field]

            extra_data = r_data.copy()
            del(extra_data[collection_field])

        else:
            obj_list = r_data
            extra_data = {}

        if not hasattr(obj_list, '__iter__'):
            raise ValueError('excpeted array-type response')

        resource_list = [cls(**obj_dict) for obj_dict in obj_list]
        return ListWithAttributes(resource_list, extra_data)

    def validate_collection_response(self, response):
        """Validate get response is valid to use for updating our object
        """

        self.validate_response(response)
        if response.status_code not in self._meta['valid_get_status']:
            raise ValueError("Expected status code in %s, got %s" %
                (self._meta['valid_get_status'], response.status_code))

    # write methods
    def update(self, **kwargs):
        """Sends a create request to the API, validating and handling any
        response received.

        :param kwargs: keyword arguments passed to get_create_url
        """
        headers = {'content-type': 'application/json'}

        url = self.get_update_url(**kwargs)
        if not url:
            raise ValueError('No update url found')

        response = self._request(self._meta['update_method'], url,
            data=self.serialize(),
            headers=headers)

        self.validate_update_response(response)
        self._full_url = url
        self.handle_update_response(response)

    def validate_update_response(self, response):

        self.validate_response(response)
        if response.status_code not in self._meta['valid_update_status']:
            raise ValueError("Invalid Update Response: expected status_code"
                        " in %s, got %s" %
                        (self._meta['valid_update_status'], response.status_code))

    def handle_update_response(self, response):
        """Handle any actions needed after a HTTP response has been validated
        for an update action

        Intended for easy subclassing. By default, attempt to update the
        current object from the response's content

        :param response: a requests.Response object
        """
        if not self._meta['update_from_write'] or not response.content:
            return

        try:
            self.update_fields(response.content)
        except ValueError:
            return

        self.handle_response(response)

    def create(self, **kwargs):
        """Sends a create request to the API, validating and handling any
        response received.

        :param kwargs: keyword arguments passed to get_create_url
        """
        headers = {'content-type': 'application/json'}

        response = self._request('POST', self.get_create_url(**kwargs),
            data=self.serialize(),
            headers=headers)

        self.validate_create_response(response)
        self.handle_create_response(response)

    def delete(self, **kwargs):
        """Sends a delete request to the API, validating and handling any
        response received.

        :param kwargs: keyword arguments passed to get_delete_url
        """
        headers = {'content-type': 'application/json'}

        response = self._request('DELETE', self.get_delete_url(**kwargs),
            headers=headers)

        self.validate_delete_response(response)
        self.handle_delete_response(response)

    def validate_create_response(self, response):

        self.validate_response(response)
        if response.status_code not in self._meta['valid_create_status']:
            raise ValueError

    def handle_create_response(self, response):
        """Handle any actions needed after a HTTP response has been validated
        for a create action

        Intended for easy subclassing. By default, attempt to update the
        current object from the response's content

        :param response: a requests.Response object
        """

        full_url = response.headers.get('location', None)
        self._full_url = full_url.replace(self._root_url, '')
        if not self._meta['update_from_write'] or not response.content:
            return

        try:
            self.update_fields(response.content)
        except ValueError:
            return

        self.handle_response(response)

    def validate_delete_response(self, response):

        self.validate_response(response)
        if response.status_code not in self._meta['valid_delete_status']:
            raise ValueError

    def handle_delete_response(self, response):
        """Handle any actions needed after a HTTP response has been validated
        for a delete action

        Intended for easy subclassing. By default, attempt to update the
        current object from the response's content

        :param response: a requests.Response object
        """

        self.resource_id = None
        self.handle_response(response)

    def save(self, **kwargs):
        """Contextually save current object. If an object can generate an
        update URL, send an update command. Otherwise, create
        """
        # this feels off to me, but it should work for now?
        if self._saved or self.full_url or self.get_update_url():
            self.update(**kwargs)
        else:
            self.create(**kwargs)

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

    def serialize(self, for_read=False):
        """Convert field data of `self` to the appropriate string serialization format

        :param for_read: include readonly fields.
        """

        serializer = self.get_serializer()
        return serializer.serialize(self.to_python(for_read=for_read))

    def deserialize(self, val_str):
        """Converts a string into a python dictionary appropriate for
        field updating

        :param val_str: python string to convert
        """

        serializer = self.get_serializer()
        obj_dict = serializer.deserialize(val_str)

        return obj_dict

    def get_serializer(self):
        return JSONSerializer()

    def validate_response(self, response):
        """
        Default validator for all response types.

        By default does nothing, but gives a all-around hook for subclasses
        to use
        """
        pass

    def handle_response(self, response):
        """
        Default handler for all response types. Ran as the last step in a
        request/response cycle
        """
        if response.use_cache:
            self.logger.debug("Setting response into cache for %s" % response.url)
            # requests.Response is not easily cached, and contains things we
            # don't need to remember. So let's cache a thin wrapper around
            # its content
            self.cache.set(response)

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
    def cache(self):
        return self._meta['cache_backend']

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
