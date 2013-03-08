import urllib


def handle_slash(url, add_slash=None):
    split = url.split('?')

    if add_slash and not split[0].endswith('/'):
        if len(split) > 1:
            url = "%s/?%s" % (split[0], split[1])
        else:
            url = "%s/" % url
    elif add_slash is False and split[0].endswith('/'):
        url = "%s?%s" % (split[0][:-1], split[1])

    return url


def make_url(base_url, params=None, add_slash=None):
    "Split off in case we need to handle more scrubing"

    base_url = handle_slash(base_url, add_slash)

    if params:
        param_string = urllib.urlencode(params)
        base_url = "%s?%s" % (base_url, param_string)

    return base_url


def is_string_like(obj):
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)
