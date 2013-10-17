class InvalidStatusError(ValueError):
    def __init__(self, valid_statuses, response):
        self.valid_statuses = valid_statuses
        self.response = response
        msg = "Expected status code in %s, got %s at %s" % (valid_statuses, response.status_code, response.url)
        super(InvalidStatusError, self).__init__(msg)


class DoesNotExist(Exception):
    pass
