import urllib


def make_url(base_url, params=None, add_slash=None):
    "Split off in case we need to handle more scrubing"
    if add_slash and not base_url.endswith('/'):
        base_url = "%s/" % base_url
    elif add_slash is False and base_url.endswith('/'):
        base_url = base_url[:-1]

    if params:
        param_string = urllib.urlencode(params)
        base_url = "%s?%s" % (base_url, param_string)

    return base_url
