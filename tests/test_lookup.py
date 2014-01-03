from nap.lookup import LookupURL


class TestLookupURL(object):

    url_string = r'xx%(hello)s%(what)s'

    def test_init(self):

        lookup_url = LookupURL(self.url_string, ('extra',))

        assert lookup_url.url_string == self.url_string
        assert lookup_url.params == ('extra',)
        assert 'hello' in lookup_url.url_vars
        assert 'what' in lookup_url.url_vars
        assert len(lookup_url.url_vars) == 2

    def test_no_params(self):
        lookup_url = LookupURL(self.url_string)
        assert lookup_url.params == []

    def test_required_vars(self):
        lookup_url = LookupURL(self.url_string, ('extra',))
        assert 'hello' in lookup_url.required_vars
        assert 'what' in lookup_url.required_vars
        assert 'extra' in lookup_url.required_vars

    def test_multiple_extra_params(self):

        lookup_url = LookupURL(self.url_string)

        url, extra = lookup_url.match(hello='hi', what='who', extra_extra=['one', 'two'])

        extra_data = extra['extra_extra']
        assert len(extra_data) == 2
        assert 'one' in extra_data
        assert 'two' in extra_data

    def test_repr(self):
        lookup_url = LookupURL(self.url_string, ('extra',))

        assert lookup_url.__unicode__() == self.url_string
        assert lookup_url.__unicode__() in str(lookup_url)
