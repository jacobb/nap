import nap


class SampleResourceModel(nap.ResourceModel):
    title = nap.Field()
    content = nap.Field()
    slug = nap.Field(resource_id=True)
    alt_name = nap.Field(api_name='some_field')

    class Meta:
        root_url = "http://foo.com/v1/"
        resource_name = 'note'
        append_urls = (
            nap.lookup.nap_url(r'%(hello)s/%(what)s/'),
            nap.lookup.nap_url(r'%(title)s/', update=True),
        )


class SampleResourceNoIdModel(nap.ResourceModel):
    title = nap.Field()
    content = nap.Field()
    slug = nap.Field()
    alt_name = nap.Field(api_name='some_field')

    class Meta:
        root_url = "http://foo.com/v1/"
        resource_name = 'note'
        append_urls = (
            nap.lookup.nap_url(r'%(hello)s/%(what)s/'),
            nap.lookup.nap_url(r'%(title)s/', update=True),
        )


class SampleResourceNoUpdateModel(nap.ResourceModel):
    title = nap.Field()
    content = nap.Field()
    slug = nap.Field(resource_id=True)
    alt_name = nap.Field(api_name='some_field')

    class Meta:
        root_url = "http://foo.com/v1/"
        resource_name = 'note'
        append_urls = (
            nap.lookup.nap_url(r'%(hello)s/%(what)s/'),
            nap.lookup.nap_url(r'%(title)s/', update=True),
        )
        update_from_write = False


class AuthorModel(nap.ResourceModel):
    name = nap.Field()
    email = nap.Field(default=None)

    class Meta:
        root_url = "http://foo.com/v1/"
