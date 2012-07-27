from nap.utils import make_url


def test_url():
    url = make_url("http://www.google.com/", params={'x': '1'})
    assert url == "http://www.google.com/?x=1"


def test_no_params():
    url = make_url("http://www.google.com/")
    assert url == "http://www.google.com/"


def test_add_slash():
    url = "http://www.google.com"
    assert make_url(url, add_slash=True) == "http://www.google.com/"
    assert make_url(url, add_slash=False) == "http://www.google.com"
    assert make_url(url, params={'x': 1}) == "http://www.google.com?x=1"

    url_s = "http://www.google.com/"
    assert make_url(url_s, add_slash=True) == "http://www.google.com/"
    assert make_url(url_s, add_slash=False) == "http://www.google.com"
    assert make_url(url_s, params={'x': 1}) == "http://www.google.com/?x=1"
