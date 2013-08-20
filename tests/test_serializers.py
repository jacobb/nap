import json

import pytest

from nap.serializers import BaseSerializer, JSONSerializer


def test_base_serializer():
    from pytest import raises

    serializer = BaseSerializer()
    with pytest.raises(NotImplementedError):
        serializer.serialize({})

    with raises(NotImplementedError):
        serializer.deserialize('{}')


class TestJSONSerializer(object):

    def get_serializer(self):
        return JSONSerializer()

    def test_serialize(self):
        sample_dict = {
            'a': 1,
            'b': 2,
        }

        serializer = self.get_serializer()

        json_str = serializer.serialize(sample_dict)

        assert json_str == '{"a": 1, "b": 2}'

    def test_deserialize(self):

        serializer = self.get_serializer()

        json_str = '{"a": 1, "b": 2}'
        json_dict = serializer.deserialize(json_str)

        assert json_dict['a'] == 1
        assert json_dict['b'] == 2