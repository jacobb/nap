import copy

from .collection import ListWithAttributes
from .exceptions import InvalidStatusError
from .http import NapRequest, NapResponse
from .serializers import JSONSerializer
from .utils import handle_slash, make_url


class ResourceEngine(object):

    def __init__(self, model):
        self.model = model
        self._tmp_request_args = {}

    def _request(self, request_method, url, *args, **kwargs):
        "Construct a NapRequest and send it via a requests.rest call"

        full_url = self.get_full_url(url)

        self.logger.info("Trying to hit %s" % full_url)

        request_args = self.get_request_args(kwargs)

        request = NapRequest(request_method, full_url, *args, **request_args)

        for mw in self.model._meta['middleware']:
            request = mw.handle_request(request)

        resource_response = request.send()
        response = NapResponse(
            url=request.url,
            status_code=resource_response.status_code,
            headers=resource_response.headers,
            content=resource_response.content,
            request_method=request_method,
        )

        for mw in reversed(self.model._meta['middleware']):
            response = mw.handle_response(request, response)

        return response

    # url methods
    def _generate_url(self, url_type='lookup', resource_obj=None, **kwargs):
        """Iterates through object's URL list to find an approrpiate match
        between ``url_type`` and ``kwargs

        :param url_type: string representing the type of URL to find. options \
        are "lookup", "create", "update" and "collection"
        :param kwargs: additional variables to pass to the LookupURL's match method
        """
        valid_urls = [
            url for url in self.model._meta['urls']
            if getattr(url, url_type, False)
        ]
        for url in valid_urls:
            field_values = dict([
                (var, getattr(resource_obj, var))
                for var in url.required_vars
                if getattr(resource_obj, var, None)
            ])

            # handle resource_id fields
            resource_id_name = self.model._meta.get('resource_id_field_name')
            if resource_id_name in kwargs and 'resource_id' in url.required_vars:
                kwargs['resource_id'] = kwargs[resource_id_name]
                if resource_id_name not in url.required_vars:
                    del kwargs[resource_id_name]

            model_keywords = {
                'resource_name': self.model._meta['resource_name']
            }

            url_match_vars = dict([
                (k, v) for (k, v) in model_keywords.items()
                if k in url.url_vars
            ])

            url_match_vars.update(field_values)
            url_match_vars.update(kwargs)

            base_url, params = url.match(**url_match_vars)

            if base_url:
                full_url = make_url(
                    base_url,
                    params=params,
                    add_slash=self.model._meta['add_slash']
                )

                return full_url

        raise ValueError("No valid url")

    def get_lookup_url(self, resource_obj=None, **kwargs):
        """Generate a URL suitable for get requests based on ``kwargs``
        Alternatively, look up a canonical GET uri for given `resource_obj`

        :param kwargs: URL lookup variables
        :param resource_obj: Resource to determine a canonical GET uri
        """
        return self._generate_url(resource_obj=resource_obj, **kwargs)

        raise ValueError("no valid URL for lookup found")

    def get_update_url(self, resource_obj=None, **kwargs):
        """Generate a URL suitable for update requests based on ``kwargs``

        :param kwargs: URL lookup variables
        """

        full_url = getattr(resource_obj, 'full_url', None)
        if full_url:
            return full_url

        try:
            update_url = self._generate_url(url_type='update', resource_obj=resource_obj, **kwargs)
        except ValueError:
            update_url = None

        return update_url

    def get_create_url(self, resource_obj=None, **kwargs):
        """Generate a URL suitable for create requests based on ``kwargs``

        :param kwargs: URL lookup variables
        """
        return self._generate_url(url_type='create', resource_obj=resource_obj, **kwargs)

    def get_delete_url(self, resource_obj=None, **kwargs):
        """Generate a URL suitable for delete requests based on ``kwargs``

        By default, this is the first valid update URL.

        :param kwargs: URL lookup variables
        """
        return self._generate_url(url_type='update', resource_obj=resource_obj, **kwargs)

    # access methods
    def get(self, uri=None, skip_cache=False, **kwargs):
        """Issues a get request to the API. If ``uri`` is passed, will send a
        request directly to that URL. otherwise, attempt a lookup request.

        :param uri: a string representing an API uri
        :param kwargs: optional variables to send to
            :meth:`~nap.resources.ResourceClass.lookup`
        """

        if uri:
            return self.get_from_uri(uri, skip_cache=skip_cache)

        return self.lookup(skip_cache=skip_cache, **kwargs)

    def lookup(self, skip_cache=False, **lookup_vars):
        """Creates a get request to the API to the first URL found based on
        ``lookup_vars``

        :param lookup_vars: variables to send to get_lookup_url
        """

        uri = self.get_lookup_url(**lookup_vars)
        return self.get_from_uri(uri, skip_cache=skip_cache)

    def get_from_uri(self, url, skip_cache=False, *args, **kwargs):
        """instance method to perform all non-collection get requests
        """
        cleaned_url = handle_slash(url, self.model._meta['add_slash'])

        if skip_cache:
            cached_response = None
        else:
            cached_response = self.get_from_cache('GET', cleaned_url)

        if cached_response:
            response = cached_response
        else:
            response = self._request('GET', cleaned_url, *args, **kwargs)

        self.validate_get_response(response)
        self.handle_get_response(response)

        # should this be handled by handle_get_response? i think probably.
        obj = self.obj_from_response(response)

        obj._full_url = cleaned_url
        return obj

    def validate_get_response(self, response):
        """Validate get response is valid to use for updating our object
        """

        self.validate_response(response)
        if response.status_code not in self.model._meta['valid_get_status']:
            raise InvalidStatusError(self.model._meta['valid_get_status'], response)

    def handle_get_response(self, response):
        """Handle any actions needed after a HTTP Response has ben validated
        for a get (get, refresh, lookup) action
        """
        resource_data = self.deserialize(response.content)

        self._raw_response_content = resource_data
        self.handle_response(response)

    # collection access methods

    def get_collection_url(self, **kwargs):
        """Generate a URL suitable for collection requests based on ``kwargs``

        By default, this is the first valid collection URL.

        :param kwargs: URL lookup variables
        """

        url = self._generate_url(url_type='collection', **kwargs)
        return url

    def all(self):
        """Creates a get request to the API to the first collection URL with
        no parameters passed
        """
        return self.filter()

    def filter(self, **lookup_vars):
        """
        Accesses the first URL set as a collections URL with no additional
        parameters passed. Returns a list of current ResourceModel objects

        :param lookup_vars: variables to pass to _generate_url
        """
        url = self.get_collection_url(**lookup_vars)
        response = self._request('GET', url)

        self.validate_collection_response(response)

        serializer = self.get_serializer()
        r_data = serializer.deserialize(response.content)
        collection_field = self.model._meta.get('collection_field')
        if collection_field and collection_field in r_data:
            obj_list = r_data[collection_field]

            extra_data = r_data.copy()
            del(extra_data[collection_field])

        else:
            obj_list = r_data
            extra_data = {}

        if obj_list:
            try:
                obj_list[0].keys
            except (KeyError, AttributeError):
                raise ValueError('expected list of dictionaries')

        resource_list = [self.model(**obj_dict) for obj_dict in obj_list]
        return ListWithAttributes(resource_list, extra_data)

    def validate_collection_response(self, response):
        """Validate get response is valid to use for updating our object
        """

        self.validate_response(response)
        if response.status_code not in self.model._meta['valid_get_status']:
            raise InvalidStatusError(self.model._meta['valid_get_status'], response)

    # write methods
    def update(self, resource_obj, **kwargs):
        """Sends a create request to the API, validating and handling any
        response received.

        :param kwargs: keyword arguments passed to get_create_url
        """

        url = self.get_update_url(resource_obj=resource_obj, **kwargs)
        if not url:
            raise ValueError('No update url found')

        response = self._request(
            self.model._meta['update_method'], url,
            data=self.serialize(resource_obj, for_read=True)
        )

        self.validate_update_response(response)
        return self.handle_update_response(response)

    def validate_update_response(self, response):

        self.validate_response(response)
        if response.status_code not in self.model._meta['valid_update_status']:
            raise InvalidStatusError(self.model._meta['valid_update_status'], response)

    def handle_update_response(self, response):
        """Handle any actions needed after a HTTP response has been validated
        for an update action

        Intended for easy subclassing. By default, attempt to update the
        current object from the response's content

        :param response: a requests.Response object
        """
        if not self.model._meta['update_from_write'] or not response.content:
            return

        try:
            obj = self.obj_from_response(response)
        except ValueError:
            obj = None

        self.handle_response(response)

        return obj

    def create(self, resource_obj, **kwargs):
        """Sends a create request to the API, validating and handling any
        response received.

        :param kwargs: keyword arguments passed to get_create_url
        """

        new_obj_data = self.serialize(resource_obj, for_read=True)
        response = self._request(
            'POST', self.get_create_url(resource_obj, **kwargs),
            data=new_obj_data
        )

        self.validate_create_response(response)
        return self.handle_create_response(response)

    def delete(self, resource_obj, **kwargs):
        """Sends a delete request to the API, validating and handling any
        response received.

        :param kwargs: keyword arguments passed to get_delete_url
        """

        delete_url = self.get_delete_url(resource_obj, **kwargs)
        response = self._request('DELETE', delete_url)

        self.validate_delete_response(response)
        self.handle_delete_response(response)

    def validate_create_response(self, response):

        self.validate_response(response)
        if response.status_code not in self.model._meta['valid_create_status']:
            raise InvalidStatusError(self.model._meta['valid_create_status'], response)

    def handle_create_response(self, response):
        """Handle any actions needed after a HTTP response has been validated
        for a create action

        Intended for easy subclassing. By default, attempt to update the
        current object from the response's content

        :param response: a requests.Response object
        """

        if not self.model._meta['update_from_write'] or not response.content:
            return

        try:
            obj = self.obj_from_response(response)
        except ValueError:
            obj = None

        self.handle_response(response)

        return obj

    def validate_delete_response(self, response):

        self.validate_response(response)
        if response.status_code not in self.model._meta['valid_delete_status']:
            raise InvalidStatusError(self.model._meta['valid_delete_status'], response)

    def handle_delete_response(self, response):
        """Handle any actions needed after a HTTP response has been validated
        for a delete action

        Intended for easy subclassing. By default, attempt to update the
        current object from the response's content

        :param response: a requests.Response object
        """

        self.handle_response(response)

    def serialize(self, obj, for_read=False):
        """Convert field data of `self` to the appropriate string serialization format

        :param for_read: include readonly fields.
        """

        serializer = self.get_serializer()
        return serializer.serialize(obj.to_python(for_read=for_read))

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
        self._tmp_request_args = {}
        self.cache_response(response)

    def obj_from_response(self, response):
        """Update object's values to values of field_data

        :param field_data: dict-like object with 'Field Name'->'New  Value'
        """
        obj = self.model()
        serializer = self.get_serializer()
        field_data = serializer.deserialize(response.content)
        obj.update_fields(field_data)
        obj._full_url = response.url

        return obj

    def get_from_cache(self, request_method, url):
        # Handle caching, unless skipped

        if request_method not in self.model._meta['cached_methods']:
            return

        full_url = self.get_full_url(url)
        cache_key = self.cache.get_cache_key(
            model=self.model,
            url=full_url,
        )
        self.logger.debug("Trying to get cached response for %s" % cache_key)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug("Got cached response for %s" % cache_key)

            # Cached responses should not get re-cached to allow for
            # expected timeouts. Now that we've retrieved the cached
            # response, behave as if cache is turned off.
            cached_response.use_cache = False
            return cached_response

    def cache_response(self, response):
        if response.request_method not in self.model._meta['cached_methods']\
                or not response.use_cache:
            return

        cache_key = self.cache.get_cache_key(
            model=self.model,
            url=response.url,
        )

        # Cache backends are meant to possibly store more than just
        # NapResponse objects, so if future features need to cache
        # anything else it's possible.
        # Thus, we pass response both as `value` and the response
        # object
        self.cache.set(cache_key, response, response=response)

    @property
    def logger(self):
        return self.model._meta['logger']

    def get_request_args(self, request_kwargs=None):

        if not request_kwargs:
            request_kwargs = {}

        # Defined in Resource's config
        request_args = copy.deepcopy(self.model._meta['default_request_args'])

        if 'headers' in self._tmp_request_args:
            default_headers = request_args.get('headers', {})
            tmp_headers = default_headers.copy()
            tmp_headers.update(self._tmp_request_args['headers'])
            request_args['headers'] = tmp_headers

        request_args.update(request_kwargs)

        return request_args

    def modify_request(self, **kwargs):
        new_eng = self.__class__(self.model)
        new_eng._tmp_request_args.update(self._tmp_request_args)
        new_eng._tmp_request_args.update(kwargs)

        return new_eng

    @property
    def cache(self):
        return self.model._meta['cache_backend']

    def get_full_url(self, uri):
        try:
            root_url = self.model._meta['root_url']
        except KeyError:
            raise ValueError("Nap requests require root_url to be defined")

        full_url = "%s%s" % (root_url, uri)
        return full_url
