import nap


class SampleRemoteModel(nap.RemoteModel):
    title = nap.Field()
    content = nap.Field()
    alt_name = nap.Field(api_name='some_field')

    class Meta:
        root_url = "http://foo.com/v1/"
        resource_url = 'note'
