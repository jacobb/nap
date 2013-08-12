"""
Kudos to mitsuhiko for flask's configuration for inspiring much of this
"""
import logging

from .cache.base import BaseCacheBackend
from .engine import ResourceEngine


DEFAULT_CONFIG = {
    'resource_name': None,
    'urls': None,
    'root_url': None,

    'resource_id_field_name': None,
    'add_slash': True,
    'update_from_write': True,
    'update_method': 'PUT',
    'auth': (),
    'engine_class': ResourceEngine,
    'middleware': (),
    'collection_field': None,
    'valid_get_status': (200,),
    'valid_update_status': (204,),
    'valid_create_status': (201,),
    'valid_delete_status': (200, 202, 204),
    'log_level': 'CRITICAL',
    'cache_backend': BaseCacheBackend(),
    'cached_methods': ('GET', ),
    'request_args': {},
    'headers': {},
    'content_type': 'application/json'
}

REQUIRED_CONFIG = ('resource_name', 'urls')


class NapConfig(dict):

    def get_request_headers(self, config):
        """
        Figures out a "final" ditionary of arguments to pass to
        requests.request, based on configured headers and content_type.

        Stored in default_request_args to distinguish from request_args, which
        is always user set.
        """

        content_type = config['content_type']
        headers = {
            'content-type': content_type
        }
        headers.update(config['headers'])
        default_request_args = {'headers': headers}
        default_request_args.update(config['request_args'])

        return default_request_args


    def __init__(self, conf=None, **kwargs):
        if not conf:
            conf = {}

        config = DEFAULT_CONFIG.copy()

        config.update(conf)
        config.update(kwargs)

        config['default_request_args'] = self.get_request_headers(config)

        logger = logging.getLogger('nap:%s' % config['resource_name'])
        log_level = getattr(logging, config['log_level'])
        logger.setLevel(log_level)

        formatter = logging.Formatter('%(levelname)s - %(message)s')

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        config['logger'] = logger

        # Backwards compatible issue: middleware is now generic and not just
        # for auth. Add all auth to the end of middleware so they are the
        # last middleware classes ran
        config['middleware'] += config['auth']

        dict.__init__(self, config)
