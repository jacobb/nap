import itertools
import urllib


def handle_slash(url, add_slash=None):
    split = url.split('?')

    if add_slash and not split[0].endswith('/'):
        if len(split) > 1:
            url = "%s/?%s" % (split[0], split[1])
        else:
            url = "%s/" % url
    elif add_slash is False and split[0].endswith('/'):
        if len(split) > 1:
            url = "%s?%s" % (split[0][:-1], split[1])
        else:
            url = split[0][:-1]

    return url


def is_string_like(obj):
    try:
        return isinstance(obj, basestring)
    except NameError:
        return isinstance(obj, str)


def make_url(base_url, params=None, add_slash=None):
    "Split off in case we need to handle more scrubing"

    base_url = handle_slash(base_url, add_slash)

    if params:

        # If we're given an non-string iterable as a params value,
        # we want to pass in multiple instances of that param key.
        def flatten_params(k, vs):
            if not hasattr(vs, '__iter__') or is_string_like(vs):
                return ((k, vs),)
            return [(k, v) for v in vs]

        flat_params = [
            flatten_params(k, v)
            for (k, v) in params.iteritems()
        ]

        # since we can have more than one value for a single key, we use a
        # tuple of two tuples instead of a dictionary
        params_tuple = tuple(itertools.chain(*flat_params))
        param_string = urllib.urlencode(params_tuple)
        base_url = "%s?%s" % (base_url, param_string)

    return base_url
