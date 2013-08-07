from .http import NapRequest, NapResponse
from .serializers import JSONSerializer
from .utils import handle_slash


class ListWithAttributes(list):
    """
    Todo:

    Replace with ResourceRequestResult
    """
    def __init__(self, list_vals, extra_data):
        super(ListWithAttributes, self).__init__()
        self.extend(list_vals)
        self.extra_data = extra_data


class RequestManager(object):

    def __init__(self, model):
        self.model = model
