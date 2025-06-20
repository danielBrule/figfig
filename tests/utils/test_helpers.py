# import pytest
from unittest.mock import patch, MagicMock

from utils import helpers as requests_utils 

# Sample URL and user-agent
TEST_URL = "https://example.com"
FAKE_USER_AGENT = {"User-Agent": "TestAgent"}

# --------------------------
# Test: is_good_response
# --------------------------
def test_is_good_response_true():
    mock_response = MagicMock(status_code=200)
    assert requests_utils.is_good_response(mock_response) is True

def test_is_good_response_false():
    mock_response = MagicMock(status_code=404)
    assert requests_utils.is_good_response(mock_response) is False

# --------------------------
# Test: simple_get
# --------------------------
@patch("utils.helpers.requests.get")
def test_simple_get_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.url = TEST_URL
    mock_resp.content = b"<html>test</html>"
    mock_get.return_value.__enter__.return_value = mock_resp
    mock_get.return_value = mock_resp

    content = requests_utils.simple_get(TEST_URL, user_agent=FAKE_USER_AGENT)
    assert content == b"<html>test</html>"

@patch("utils.helpers.requests.get")
def test_simple_get_redirect_blocked(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.url = "https://redirected.com"
    mock_resp.content = b"<html>test</html>"
    mock_get.return_value.__enter__.return_value = mock_resp
    mock_get.return_value = mock_resp

    content = requests_utils.simple_get(TEST_URL, user_agent=FAKE_USER_AGENT, stop_if_url_different=True)
    assert content is None

@patch("utils.helpers.requests.get")
def test_simple_get_failure(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value.__enter__.return_value = mock_resp
    mock_get.return_value = mock_resp

    content = requests_utils.simple_get(TEST_URL, user_agent=FAKE_USER_AGENT)
    assert content is None

# --------------------------
# Test: get_url_redirection
# --------------------------
@patch("utils.helpers.requests.get")
def test_get_url_redirection_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.url = "https://final-url.com"
    mock_get.return_value.__enter__.return_value = mock_resp
    mock_get.return_value = mock_resp

    url = requests_utils.get_url_redirection(TEST_URL, user_agent=FAKE_USER_AGENT)
    assert url == "https://final-url.com"

@patch("utils.helpers.requests.get")
def test_get_url_redirection_failure(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_get.return_value.__enter__.return_value = mock_resp
    mock_get.return_value = mock_resp

    url = requests_utils.get_url_redirection(TEST_URL, user_agent=FAKE_USER_AGENT)
    assert url is None


# --------------------------
# Test: simple_requests_json
# --------------------------
@patch("utils.helpers.requests.request")
def test_simple_requests_json_success(mock_request):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"success": true}'
    mock_request.return_value.__enter__.return_value = mock_resp
    mock_request.return_value = mock_resp

    response = requests_utils.simple_requests_json(TEST_URL, user_agent=FAKE_USER_AGENT)
    assert response == b'{"success": true}'

@patch("utils.helpers.requests.request")
def test_simple_requests_json_failure(mock_request):
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_request.return_value.__enter__.return_value = mock_resp
    mock_request.return_value = mock_resp

    response = requests_utils.simple_requests_json(TEST_URL, user_agent=FAKE_USER_AGENT)
    assert response is None
