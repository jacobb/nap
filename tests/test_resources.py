from nap import resources


class SampleDataModel(resources.DataModel):
    x = resources.Field()
    y = resources.Field()


class TestDataModels(object):

    def test_mapping_to_fields(self):

        dm = SampleDataModel(x='a', y='b')

        assert dm.x == 'a'
        assert dm.y == 'b'
