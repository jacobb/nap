import urllib


def handle_slash(url, add_slash=None):
    if add_slash and not url.endswith('/'):
        url = "%s/" % url
    elif add_slash is False and url.endswith('/'):
        url = url[:-1]

    return url


def make_url(base_url, params=None, add_slash=None):
    "Split off in case we need to handle more scrubing"

    base_url = handle_slash(base_url, add_slash)

    if params:
        param_string = urllib.urlencode(params)
        base_url = "%s?%s" % (base_url, param_string)

    return base_url
