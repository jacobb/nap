from nap.collection import ListWithAttributes


class TestListWithAttributes(object):

    def test_acts_like_list(self):
        lwa = ListWithAttributes([1,2,3])

        assert len(lwa) == 3
        assert 1 in lwa
        assert 2 in lwa
        assert 3 in lwa

    def test_extra_data(self):
        ed = {'some_data': 'Hello'}
        lwa = ListWithAttributes([1,2,3], extra_data=ed)

        assert lwa.extra_data['some_data'] == ed['some_data']