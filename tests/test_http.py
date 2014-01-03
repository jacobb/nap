import pytest

from nap.http import NapRequest, NapResponse


class TestRequestMethods(object):

    def test_invalid_http_method(self):

        # ...for now
        invalid_method = "TARDIS"

        r = NapRequest('badurl.com/', 'POST')

        with pytest.raises(ValueError):
            r.method = invalid_method


class TestNapResponse(object):

    def test_default_headers(self):
        res = NapResponse('content', 'naprulez.org', 200)

        assert hasattr(res.headers, 'keys')
