

class ListWithAttributes(list):
    def __init__(self, list_vals, extra_data=None):

        if not extra_data:
            extra_data = {}
        super(ListWithAttributes, self).__init__(list_vals)
        self.extra_data = extra_data
