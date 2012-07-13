from slumber import API as slumber_API, url_join, Resource


class NapMixin(object):

    def __init__(self, *args, **kwargs):
        self.resource_registry = kwargs.pop('resource_registry', {})
        super(NapMixin, self).__init__(*args, **kwargs)

    def __getattr__(self, item):

        if item.startswith("_"):
            raise AttributeError(item)

        kwargs = {}
        for key, value in self._store.iteritems():
            kwargs[key] = value

        kwargs.update({"base_url": url_join(self._store["base_url"], item)})

        if item in self.resource_registry:

            default_kwargs = {
                "resource_cls": self.resource_registry[item],
                "resource_registry": self.resource_registry,
                'root_url': self._store['root_url']
            }
            kwargs.update(default_kwargs)
            return NapResource(**kwargs)
        else:
            return Resource(**kwargs)


class API(NapMixin, slumber_API):

    def __init__(self, *args, **kwargs):
        super(API, self).__init__(*args, **kwargs)
        self._store['root_url'] = kwargs.get('base_url', None)

    def register_resource(self, resource_cls, name=None):
        if not name:
            name = resource_cls._meta.name
        self.resource_registry[name] = resource_cls


class NapResource(NapMixin, Resource):

    def __init__(self, *args, **kwargs):
        self.resource_cls = kwargs.pop('resource_cls', None)
        super(NapResource, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        obj = super(NapResource, self).__call__(*args, **kwargs)
        obj.resource_cls = self.resource_cls
        return obj

    def get(self, **kwargs):
        data = super(NapResource, self).get(**kwargs)
        return self.resource_cls(**data)
