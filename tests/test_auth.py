from nap import auth
from .utils import get_nap_request


class TestBaseAuthorization(object):

    def test_dummy_methods(self):

        base_auth = auth.BaseAuthorization()

        assert base_auth.handle_request('1234') == '1234'


class TestHttpAuthorization(object):

    def test_handle_request(self):
        http_auth = auth.HttpAuthorization(username='user', password='pass')

        request = get_nap_request()

        new_request = http_auth.handle_request(request)

        assert new_request.auth == ('user', 'pass')


class TestFoauthAuthorization(object):

    def create_auth(self):
        foauth_auth = auth.FoauthAuthorization(
            email='test@email.com',
            password='123')

        return foauth_auth

    def test_handle_request(self):
        url = 'http://someurl.com/1/'
        foauth_auth = self.create_auth()
        request = get_nap_request(url='http://someurl.com/1/')

        new_request = foauth_auth.handle_request(request)
        assert foauth_auth.orig_url == url
        assert new_request.url == 'https://foauth.org/someurl.com/1/'
        assert new_request.auth == (foauth_auth.email, foauth_auth.password)

        # assert method hasn't changed
        assert new_request.method == 'GET'

    def test_handle_request_with_patch(self):
        request = get_nap_request(method='PATCH')
        foauth_auth = self.create_auth()

        new_request = foauth_auth.handle_request(request)

        assert new_request.method == 'POST'
        assert new_request.headers['X-HTTP-Method-Override'] == 'PATCH'
