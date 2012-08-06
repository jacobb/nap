import nap


class User(nap.ResourceModel):
    pass


class Tweet(nap.ResourceModel):
    id = nap.Field()
    text = nap.Field()

    class Meta:
        root_url = "https://api.twitter.com/1/"
        resource_name = "statuses"
        add_slash = False
        urls = (
            nap.nap_url("%(resource_name)s/show.json",
                params=('id',), lookup=True),
        )
