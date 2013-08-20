import json

import mock

from . import SampleResourceModel
from nap.middleware import BaseMiddleware

class TestMiddleware(BaseMiddleware):

    def handle_request(self, request):
        request.headers.update({'fake_header': 'fake_value'})
        return request

    def handle_response(self, request, response):
        response.headers.update({'fake_header': 'fake_response_value'})
        return response


class TestBaseMiddleware(object):

    def get_rm(self, **kwargs):
        rm = SampleResourceModel(**kwargs)
        rm._meta['middleware'] += TestMiddleware(),

        return rm

    def test_handle_request(self):
        rm = self.get_rm()
        fake_dict = {
            'title': "A fake title",
            'content': "isnt this neat",
        }
        with mock.patch('requests.request') as r:
            stubbed_response = mock.Mock()

            stubbed_response.status_code = 200
            stubbed_response.content = json.dumps(fake_dict)
            r.return_value = stubbed_response

            rm.objects._request('GET', 'some_url')

            request_kwargs = r.call_args[1]
            assert request_kwargs['headers']['fake_header'] == 'fake_value'

    def test_handle_response(self):
        rm = self.get_rm()
        fake_dict = {
            'title': "A fake title",
            'content': "isnt this neat",
        }
        with mock.patch('requests.request') as r:
            stubbed_response = mock.Mock()

            stubbed_response.status_code = 200
            stubbed_response.headers = {'content-type': 'application/json'}
            stubbed_response.content = json.dumps(fake_dict)
            r.return_value = stubbed_response

            response = rm.objects._request('GET', 'some_url')

        headers = response.headers
        assert headers['fake_header'] == 'fake_response_value'
