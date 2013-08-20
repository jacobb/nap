import pytest

from nap.http import NapRequest


class TestRequestMethods(object):

    def test_invalid_http_method(self):

        # ...for now
        invalid_method = "TARDIS"

        r = NapRequest('badurl.com/', 'POST')

        with pytest.raises(ValueError):
            r.method = invalid_method
