import json


class BaseSerializer(object):

    def serialize(self):
        raise NotImplementedError

    def deserialize(self):
        raise NotImplementedError


class JSONSerializer(object):

    def serialize(self, val_dict):

        return json.dumps(val_dict)

    def deserialize(self, val_str):

        return json.loads(val_str)
