from nap import resources


class SampleDataModel(resources.DataModel):
    x = resources.Field()
    y = resources.Field()


class TestDataModels(object):

    def test_mapping_to_fields(self):

        dm = SampleDataModel(x='a', y='b')

        assert dm.x == 'a'
        assert dm.y == 'b'
        assert len(dm.extra_data) == 0

    def test_extra_data(self):

        dm = SampleDataModel(x='a', y='b', z='c')

        assert dm.extra_data['z'] == 'c'
