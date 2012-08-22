from nap.conf import NapConfig, DEFAULT_CONFIG


def test_config_defaults():
    config = NapConfig()

    for key, value in DEFAULT_CONFIG.iteritems():
        assert config[key] == value


def test_config_override():

    new_options = {
        'override_methood': 'PATCH',
        'add_slash': False,
    }

    config = NapConfig(
        new_options,
        collection_field='objects',
        override_method='POST'
    )

    assert config['override_method'] == 'POST'
    assert config['collection_field'] == 'objects'
    assert config['add_slash'] == False


def test_config_from_class():

    class Meta:
        resource_name = 'gists'
        root_url = 'https://api.github.com/'

    config = NapConfig()
    config.from_class(Meta)

    assert config['resource_name'] == 'gists'
    assert config['root_url'] == 'https://api.github.com/'
