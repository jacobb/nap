import nap
from nap.auth import FoauthAuthorization

import requests

import secret


class GistFile(nap.ResourceModel):
    size = nap.Field(readonly=True)
    # filename = nap.Field()
    raw_url = nap.Field(readonly=True)
    content = nap.Field()

    class Meta:
        root_url = 'https://api.github.com/gists'


class Gist(nap.ResourceModel):
    url = nap.Field(readonly=True)
    id = nap.Field(resource_id=True)
    description = nap.Field()
    public = nap.Field()
    user = nap.Field()
    html_url = nap.Field(readonly=True)
    files = nap.DictField(GistFile)

    class Meta:
        resource_name = 'gists'
        root_url = 'https://api.github.com/'
        add_slash = False
        update_method = requests.patch
        additional_urls = '%(resource_name)s/%(gist_property)s'
        auth = (
            FoauthAuthorization(secret.foauth_email, secret.foauth_password),
        )


# gf = GistFile(content='test')
# g = Gist(description="nap test", files={'what.txt': gf}, public=True)
# g.save()
# g.html_url
