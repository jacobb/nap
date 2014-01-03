from nap.utils import make_url, is_string_like, handle_slash


def test_url():
    url = make_url("http://www.naprulez.org/", params={'x': '1'})
    assert url == "http://www.naprulez.org/?x=1"


def test_no_params():
    url = make_url("http://www.naprulez.org/")
    assert url == "http://www.naprulez.org/"


def test_multiple_params():
    url = make_url("http://www.naprulez.org/", params={'x': ['1', '2']})
    assert url == "http://www.naprulez.org/?x=1&x=2"


def test_add_slash():
    url = "http://www.naprulez.org"
    assert make_url(url, add_slash=True) == "http://www.naprulez.org/"
    assert make_url(url, add_slash=False) == "http://www.naprulez.org"
    assert make_url(url, params={'x': 1}) == "http://www.naprulez.org?x=1"

    url_s = "http://www.naprulez.org/"
    assert make_url(url_s, add_slash=True) == "http://www.naprulez.org/"
    assert make_url(url_s, add_slash=False) == "http://www.naprulez.org"
    assert make_url(url_s, params={'x': 1}) == "http://www.naprulez.org/?x=1"


def test_stringlike():

    assert is_string_like('hello') is True
    assert is_string_like(u'hello') is True
    assert is_string_like(123) is False


class TestHandleTest(object):

    def test_has_get_params(self):
        uri = "something.com?q=bob&x=sue"
        new_uri = handle_slash(uri, add_slash=True)
        assert new_uri == "something.com/?q=bob&x=sue"

        new_uri = handle_slash(uri)
        assert new_uri == "something.com?q=bob&x=sue"

    def has_get_params_ends_in_slash(self):
        uri = "something.com/?q=bob&x=sue"
        new_uri = handle_slash(uri, add_slash=False)
        assert new_uri == "something.com?q=bob&x=sue"