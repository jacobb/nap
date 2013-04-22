"""
Kudos to mitsuhiko for flask's configuration for inspiring much of this
"""
import logging

from .cache.base import BaseCacheBackend


DEFAULT_CONFIG = {
    'resource_name': None,
    'urls': None,
    'root_url': None,

    'resource_id_field_name': None,
    'add_slash': True,
    'update_from_write': True,
    'update_method': 'PUT',
    'auth': (),
    'collection_field': None,
    'valid_get_status': (200,),
    'valid_update_status': (204,),
    'valid_create_status': (201,),
    'valid_delete_status': (200, 202, 204),
    'log_level': 'CRITICAL',
    'cache_backend': BaseCacheBackend(),
    'cached_methods': ('GET', ),
}

REQUIRED_CONFIG = ('resource_name', 'urls')


class NapConfig(dict):

    def __init__(self, conf=None, **kwargs):
        if not conf:
            conf = {}

        config = DEFAULT_CONFIG.copy()

        config.update(conf)
        config.update(kwargs)
        logger = logging.getLogger('nap:%s' % config['resource_name'])
        log_level = getattr(logging, config['log_level'])
        logger.setLevel(log_level)

        formatter = logging.Formatter('%(levelname)s - %(message)s')

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        config['logger'] = logger

        dict.__init__(self, config)

    def from_class(self, options):
        """Convenience function to support the potentially deprecated use of
        class Meta
        """
        for key in dir(options):
            self[key] = getattr(options, key)
