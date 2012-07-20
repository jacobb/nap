from nap.utils import make_url


def test_url():
    url = make_url("http://www.google.com", params={'x': '1'})
    assert url == "http://www.google.com/?x=1"


def test_no_params():
    url = make_url("http://www.google.com")
    assert url == "http://www.google.com/"
