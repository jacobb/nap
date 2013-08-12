import json
import unittest

import nap
from nap.engine import ResourceEngine

import mock

from . import SampleResourceModel



class TestResourceEngineAccessMethods(object):

    def get_engine(self):
        engine = ResourceEngine(SampleResourceModel)
        return engine

    def test_get_from_uri(self):

        self.engine = self.get_engine()
        fake_dict = {
            'title': "A fake title",
            'content': "isnt this neat",
        }
        with mock.patch('requests.request') as get:
            stubbed_response = mock.Mock()
            stubbed_response.content = json.dumps(fake_dict)

            model_root_url = self.engine.model._meta['root_url']
            expected_url = "xyz/"
            stubbed_response.url = expected_url
            stubbed_response.status_code = 200

            get.return_value = stubbed_response
            obj = self.engine.get_from_uri('xyz')

            assert obj.title == fake_dict['title']
            assert obj.content == fake_dict['content']
            assert obj._root_url == model_root_url
            assert obj._full_url == expected_url

    def test_get(self):

        self.engine = self.get_engine()
        with mock.patch('nap.engine.ResourceEngine.get_from_uri') as g:
            self.engine.get('/some/uri/')
            g.assert_called_once
        with mock.patch('nap.engine.ResourceEngine.lookup') as lookup:
            self.engine.get(pk=1)
            lookup.assert_called_once

    def test_get_lookup_url(self):

        self.engine = self.get_engine()
        final_uri = self.engine.get_lookup_url(hello='1', what='2')
        assert final_uri == "1/2/"

        final_uri_with_params = self.engine.get_lookup_url(
            hello='1',
            what='2',
            extra_param='3'
        )
        assert final_uri_with_params == '1/2/?extra_param=3'
        # assert params == {'extra_param': '3'}
        SampleResourceModel._lookup_urls = []

    def test_lookup(self):

        self.engine = self.get_engine()
        with mock.patch('nap.engine.ResourceEngine.get_from_uri') as get:
            self.engine.lookup(hello='hello_test', what='what_test')
            get.assert_called_with('hello_test/what_test/')

        SampleResourceModel._lookup_urls = []

    def test_lookup_no_valid_urls(self):

        self.engine = self.get_engine()
        from pytest import raises
        with raises(ValueError):
            self.engine.get_lookup_url(hello='bad_hello')

        SampleResourceModel._lookup_urls = []

    def test_generate_url(self):

        self.engine = self.get_engine()
        rm = self.engine.model(hello='1', slug='slug')
        assert self.engine._generate_url(url_type='create', resource_obj=rm) == 'note/'

        # assert that keyword arguments take precedence over meta arguments
        essay_url = rm.objects._generate_url(url_type='create', resource_name='essay')
        assert essay_url == 'essay/'

        assert rm.objects._generate_url(url_type='update') == 'note/slug/'
        # assert that keyword arguments take predecnce over field values
        new_slug_url = rm._generate_url(url_type='update', slug='new-slug')
        assert new_slug_url == 'note/new-slug/'

#     def test_refresh(self):
#         rm = SampleResourceModel(pk=5, title="bad title")
#         with mock.patch('requests.request') as request:
#             r = mock.Mock()
#             r.content = json.dumps({'title': 'new title'})
#             r.status_code = 200
#             request.return_value = r
#             rm.refresh()
#             assert request.called

#         assert rm.title == 'new title'


# class TestResourceCollectionMethods(object):

#     def test_collection_field(self):

#         SampleResourceModel._meta['collection_field'] = 'objects'
#         with mock.patch('requests.request') as request:
#             r = mock.Mock()
#             collection_dict = {
#                 'meta': {'something': True},
#                 'objects': [
#                     {'title': 'a'},
#                     {'title': 'b', 'content': "b's content"},
#                     {'title': 'c'},
#                 ]
#             }
#             r.content = json.dumps(collection_dict)
#             r.status_code = 200
#             request.return_value = r
#             objects = SampleResourceModel.all()
#             assert request.called
#         assert len(objects) == 3
#         SampleResourceModel._meta['collection_field'] = None


# class TestSerialize(object):

#     def test_serialize(self):
#         dm = SampleResourceModel(
#             slug='123',
#             title='test title',
#             content='test content'
#         )
#         json_string = dm.serialize()
#         obj_dict = json.loads(json_string)
#         assert obj_dict['title'] == 'test title'
#         assert obj_dict['content'] == 'test content'
#         assert obj_dict['alt_name'] == None
#         assert 'slug' not in obj_dict

#     def test_serialize_for_write_false(self):
#         dm = SampleResourceModel(
#             slug='123',
#             title='test title',
#             content='test content'
#         )
#         json_string = dm.serialize(for_read=True)
#         obj_dict = json.loads(json_string)
#         assert obj_dict['title'] == 'test title'
#         assert obj_dict['content'] == 'test content'
#         assert obj_dict['alt_name'] == None
#         assert obj_dict['slug'] == '123'


# class TestResourceModelWriteMethods(unittest.TestCase):

#     headers = {'content-type': 'application/json'}

#     def tearDown(self):
#         SampleResourceModel._lookup_urls = []

#     def dont_test_write_url(self):

#         dm = SampleResourceModel(
#             title='expected_title',
#             content='Blank Content')

#         url = dm.get_update_url()
#         assert url == u'expected_title/'
#         SampleResourceModel._lookup_urls = []

#     def test_create_url(self):

#         class CreateURLModel(nap.ResourceModel):
#             class Meta:
#                 root_url = 'http://www.foo.com/api/'

#         cm = CreateURLModel()

#         assert cm.get_create_url() == 'createurlmodel/'

#         class CreateURLModelTwo(nap.ResourceModel):
#             class Meta:
#                 root_url = 'http://www.foo.com/api/'
#                 resource_name = 'note'

#         cm2 = CreateURLModelTwo()
#         assert cm2.get_create_url() == 'note/'

#     def test_save(self):
#         dm = SampleResourceModel(
#             title=None,
#             content='Blank Content')
#         with mock.patch('nap.engine.ResourceEngine.create') as create:
#             dm.save()
#             assert create.called
#         dm._full_url = 'http://www.foo.com/v1/1/'
#         with mock.patch('nap.engine.ResourceEngine.update') as update:
#             dm.save()
#             assert update.called

#     def test_update(self):
#         dm = SampleResourceModel(
#             title='expected_title',
#             content='Blank Content')
#         with mock.patch('requests.request') as put:
#             r = mock.Mock()
#             r.content = ''
#             r.status_code = 204
#             put.return_value = r
#             dm.update()
#             put.assert_called_with('PUT', "http://foo.com/v1/expected_title/",
#                 data=dm.serialize(), headers=self.headers, auth=None)
#         SampleResourceModel._lookup_urls = []

#     def test_handle_update_response(self):
#         dm = SampleResourceModel(title='old title')
#         dm._full_url = 'http://foo.com/v1/random_title/'
#         with mock.patch('requests.request') as put:
#             r = mock.Mock()
#             r.content = json.dumps({'title': 'hello', 'content': 'content'})
#             r.status_code = 204
#             put.return_value = r
#             dm.update()
#         assert dm.title == 'hello'
#         assert dm.content == 'content'

#     def test_create(self):

#         # add a lookup url to ensure it doesn't get used
#         dm = SampleResourceModel(
#             title='expected_title',
#             content='Blank Content')
#         with mock.patch('requests.request') as post:
#             r = mock.Mock()
#             r.content = ''
#             r.headers = {'location': 'http://foo.com/v1/random_title/'}
#             r.status_code = 201
#             post.return_value = r
#             dm.create()
#             post.assert_called_with('POST', "http://foo.com/v1/note/",
#                 data=dm.serialize(), headers=self.headers, auth=None)
#         SampleResourceModel._lookup_urls = []

#     def test_handle_create_response(self):
#         dm = SampleResourceModel(title='old title')
#         with mock.patch('requests.request') as post:
#             r = mock.Mock()
#             r.content = json.dumps({'title': 'hello', 'content': 'content'})
#             r.status_code = 201
#             post.return_value = r
#             dm.create()

#         assert dm.title == 'hello'
#         assert dm.content == 'content'

#     def test_filter(self):
#         with mock.patch('requests.request') as request:
#             r = mock.Mock()
#             r.status_code = 200
#             r.content = json.dumps([
#                 {'title': 'hello', 'content': 'content'},
#                 {'title': 'hello', 'content': 'content'}
#             ])
#             request.return_value = r
#             dms = SampleResourceModel.filter(title='title')

#         assert len(dms) == 2

#     def test_write_with_no_lookup_url(self):

#         from pytest import raises

#         dm = SampleResourceModel(content='what')
#         with raises(ValueError):
#             dm.update()


# class TestResourceID(object):

#     def test_resource_id_get(self):
#         dm = SampleResourceModel(
#             title='expected_title',
#             content='Blank Content',
#             slug='some-slug')

#         assert dm.resource_id == 'some-slug'

#     def test_resource_id_set(self):
#         dm = SampleResourceModel(
#             title='expected_title',
#             content='Blank Content',
#             slug='some-slug')

#         dm.resource_id = 'a-new-slug'

#         assert dm.slug == 'a-new-slug'

#     def test_resource_id_lookup(self):
#         resource_id_url = SampleResourceModel.get_lookup_url(slug='some-slug')

#         assert resource_id_url == 'note/some-slug/'


# class TestReourceEtcMethods(object):

#     def test_repr(self):

#         dm = SampleResourceModel(slug='some-slug')
#         assert str(dm) == '<SampleResourceModel: some-slug>'


# class TestResourceAuth(object):

#     def test_meta_set(self):
#         # SampleResourceModel
#         pass
