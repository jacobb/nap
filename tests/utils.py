from nap.http import NapRequest


def get_nap_request(method='GET', url='http://www.foo.com',
        headers=None, auth=None, *args, **kwargs):

    """
    Fake a NapRequest
    """
    request = NapRequest(method, url, headers, auth, *args, **kwargs)

    return request
