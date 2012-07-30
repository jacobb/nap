import nap
from nap.auth import FoauthAuthorization
from nap.lookup import nap_url

import secret


class GistFile(nap.ResourceModel):
    content = nap.Field()

    size = nap.Field(readonly=True)
    raw_url = nap.Field(readonly=True)

    class Meta:
        root_url = 'https://api.github.com/gists'


class Gist(nap.ResourceModel):
    id = nap.Field(resource_id=True)

    description = nap.Field()
    public = nap.Field()
    files = nap.DictField(GistFile)

    url = nap.Field(readonly=True)
    user = nap.Field(readonly=True)
    html_url = nap.Field(readonly=True)

    class Meta:
        resource_name = 'gists'
        root_url = 'https://api.github.com/'
        add_slash = False
        update_method = 'PATCH'
        prepend_urls = (
            # For accessing /gists/starred and /gists/public, eg.
            # Gist.filter(property='starred')
            nap_url('%(resource_name)s/%(property)s', collection=True, lookup=False),
        )
        auth = (
            FoauthAuthorization(secret.foauth_email, secret.foauth_password),
        )


# gf = GistFile(content='test')
# g = Gist(description="nap test", files={'what.txt': gf}, public=True)
# g.save()
# g.html_url
