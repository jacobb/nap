import mock

from nap.exceptions import InvalidStatusError


def test_invalid_status():
    statuses = (200, 201)
    response = mock.Mock()
    response.status_code = 404
    response.url = "naprulez.org"
    e = InvalidStatusError(statuses, response)
    try:
        raise e
    except InvalidStatusError as e:
        expected = InvalidStatusError.ERROR_MSG % (statuses, 404, "naprulez.org")
        assert str(e) == expected
