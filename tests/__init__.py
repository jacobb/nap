import nap


class SampleRemoteModel(nap.RemoteModel):
    title = nap.Field()
    content = nap.Field()
    alt_name = nap.Field(api_name='some_field')

    class Meta:
        root_url = "http://foo.com/v1/"
        resource_name = 'note'
        additional_urls = (
            nap.lookup.nap_url(r'(?P<hello>\d*)/(?P<what>.*)/'),
            nap.lookup.nap_url(r'(?P<title>[^/]+)/', update=True),
        )
