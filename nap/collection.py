

class ListWithAttributes(list):
    def __init__(self, list_vals, extra_data):
        super(ListWithAttributes, self).__init__()
        self.extend(list_vals)
        self.extra_data = extra_data