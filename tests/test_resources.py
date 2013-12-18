import json
import unittest

import nap

import mock

from . import SampleResourceModel, SampleResourceNoIdModel


class TestResourceModelCreation(object):

    def test_mapping_to_fields(self):

        dm = SampleResourceModel(title='a', content='b')

        assert dm.title == 'a'
        assert dm.content == 'b'
        assert len(dm.extra_data) == 0

    def test_extra_data(self):

        dm = SampleResourceModel(title='a', note='b', z='c')

        assert dm.extra_data['z'] == 'c'
        assert not hasattr(dm, 'z')

    def test_api_name(self):
        dm = SampleResourceModel(title='a', note='b', some_field='c')

        assert dm.alt_name == 'c'

    def test_meta_attached(self):

        class SampleMetaDataModel(nap.ResourceModel):
            class Meta:
                resource_name = 'bob'
                root_url = "http://foo.com/v1/"

        dm = SampleMetaDataModel()

        assert dm._meta['resource_name'] == 'bob'
        assert dm._meta['root_url'] == "http://foo.com/v1/"

    def test_override_root_url(self):

        different_url = "http://www.differenturl.com/v1/"
        dm = SampleResourceModel(root_url=different_url)
        assert dm._root_url == different_url


class TestResourceSave(object):

    def test_save(self):
        dm = SampleResourceModel(
            title=None,
            content='Blank Content')
        with mock.patch('nap.engine.ResourceEngine.create') as create:
            dm.save()
            assert create.called
        dm._full_url = 'http://www.foo.com/v1/1/'
        with mock.patch('nap.engine.ResourceEngine.update') as update:
            dm.save()
            assert update.called

class TestResourceID(object):

    def test_resource_id_get(self):
        dm = SampleResourceModel(
            title='expected_title',
            content='Blank Content',
            slug='some-slug')

        assert dm.resource_id == 'some-slug'

    def test_no_resource_id_get(self):
        dm = SampleResourceNoIdModel(
            slug='some-slug',
        )

        assert dm.resource_id is None

    def test_no_resource_id_get(self):
        dm = SampleResourceNoIdModel(
            slug='some-slug',
        )

        dm.resource_id = "Hello"
        assert dm.resource_id is None

    def test_resource_id_set(self):
        dm = SampleResourceModel(
            title='expected_title',
            content='Blank Content',
            slug='some-slug')

        dm.resource_id = 'a-new-slug'

        assert dm.slug == 'a-new-slug'


class TestReourceEtcMethods(object):

    def test_repr(self):

        dm = SampleResourceModel(slug='some-slug')
        assert str(dm) == '<SampleResourceModel: some-slug>'

    def test_logger(self):
        dm = SampleResourceModel(slug='some-slug')
        assert dm.logger == dm._meta['logger']

    def test_eq(self):
        dm = SampleResourceModel(slug='some-slug')
        dm2 = SampleResourceModel(slug='some-slug')
        dm3 = SampleResourceModel(slug='some-other-slug')

        assert dm == dm2
        assert dm != dm3


class TestResourceAuth(object):

    def test_meta_set(self):
        # SampleResourceModel
        pass
