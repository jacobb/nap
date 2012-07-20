from nap.lookup import LookupURL


class TestLookupURL(object):

    pattern = r'xx(?P<hello>\d*)(?P<what>.*)'

    def test_init(self):

        lookup_url = LookupURL(self.pattern, ('extra',))

        assert lookup_url.pattern == self.pattern
        assert lookup_url.params == ('extra',)
        assert 'hello' in lookup_url.url_parts
        assert 'what' in lookup_url.url_parts
        assert len(lookup_url.url_parts) == 2

    def test_no_params(self):
        lookup_url = LookupURL(self.pattern)
        assert lookup_url.params == []

    def test_required_vars(self):
        lookup_url = LookupURL(self.pattern, ('extra',))
        assert 'hello' in lookup_url.required_vars
        assert 'what' in lookup_url.required_vars
        assert 'extra' in lookup_url.required_vars
