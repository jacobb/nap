import urllib


def make_url(base_url, params=None, add_slash=True):
    "Split off in case we need to handle more scrubing"
    if add_slash and not base_url.endswith('/'):
        base_url = "%s/" % base_url

    if params:
        param_string = urllib.urlencode(params)
        base_url = "%s?%s" % (base_url, param_string)

    return base_url
