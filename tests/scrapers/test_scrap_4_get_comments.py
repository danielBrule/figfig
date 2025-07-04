import hashlib
import json
import pytest
from unittest.mock import patch, MagicMock
from scrapers.scrap_4_get_comments import CommentsScraper  # Replace with the actual module path

# ✅ Patch env variable globally for all tests in this file
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("SERVICEBUS_CONNECTION_STRING", "Endpoint=sb://fake/;SharedAccessKeyName=fake;SharedAccessKey=fake-key")
    monkeypatch.setenv("APP_ENV", "dev")

@pytest.fixture(autouse=True)
def mock_key_vault_secret():
    with patch("azure.keyvault.secrets.SecretClient.get_secret") as mock_get_secret:
        mock_get_secret.return_value.value = "fake-password"
        yield

# -----------------------
# Test: _get_author & _get_author_type
# -----------------------
def test_get_author_and_type():
    scraper = CommentsScraper()
    scraper._article_id = 123

    author = {"username": "johndoe", "__typename": "UserType"}
    expected_hash = hashlib.md5("johndoe".encode("utf-8")).hexdigest()

    assert scraper._get_author(author) == expected_hash
    assert scraper._get_author_type(author) == "UserType"

    assert scraper._get_author(None) == ""
    assert scraper._get_author_type(None) == ""

# -----------------------
# Test: _get_article_uid
# -----------------------
@patch("scrapers.scrap_4_get_comments.Session")  # Adjust path as needed
@patch("scrapers.scrap_4_get_comments.get_engine")
def test_get_article_uid(mock_engine, mock_session_class):
    scraper = CommentsScraper()
    scraper._article_id = 1

    mock_session = MagicMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = "uid-xyz"
    mock_session_class.return_value.__enter__.return_value = mock_session

    scraper._get_article_uid()
    assert scraper._articles_uid == "uid-xyz"

# -----------------------
# Test: _get_replies
# -----------------------
@patch("scrapers.scrap_4_get_comments.simple_get")
def test_get_replies(mock_simple_get):
    scraper = CommentsScraper()
    scraper._article_id = 1

    reply_data = {
        "data": {
            "commentReplies": [
                {
                    "id": "r1",
                    "text": "Reply 1",
                    "createdAt": "2024-06-01T10:00:00Z",
                    "repliesCount": 0,
                    "author": {"username": "replier", "__typename": "User"}
                }
            ]
        }
    }
    mock_simple_get.return_value = json.dumps(reply_data)

    scraper._get_replies("parent-123")

    assert len(scraper._comments) == 1
    assert scraper._comments[0].id == "r1"
    assert scraper._comments[0].parent_id == "parent-123"

# -----------------------
# Test: _get_articles_comments
# -----------------------
@patch("scrapers.scrap_4_get_comments.simple_get")
def test_get_articles_comments(mock_simple_get):
    scraper = CommentsScraper()
    scraper._article_id = 1
    scraper._articles_uid = "uid-abc"

    mock_simple_get.side_effect = [
        json.dumps({
            "data": {
                "comments": [
                    {
                        "id": "c1",
                        "text": "Main comment",
                        "createdAt": "2024-06-01T12:00:00Z",
                        "repliesCount": 0,
                        "author": {"username": "author", "__typename": "User"}
                    }
                ]
            }
        }),
        json.dumps({"data": {"comments": []}})
    ]

    scraper._get_articles_comments()

    assert len(scraper._comments) == 1
    assert scraper._comments[0].id == "c1"

# -----------------------
# Test: _add_new_comments
# -----------------------
@patch("scrapers.scrap_4_get_comments.Session")
@patch("scrapers.scrap_4_get_comments.get_engine")
def test_add_new_comments(mock_engine, mock_session_class):
    scraper = CommentsScraper()
    scraper._article_id = 1
    mock_comment = MagicMock()
    scraper._comments = [mock_comment]

    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session

    scraper._add_new_comments()

    mock_session.add_all.assert_called_once_with([mock_comment])
    mock_session.commit.assert_called_once()

# -----------------------
# Test: _update_stage (success)
# -----------------------
@patch("scrapers.scrap_4_get_comments.Session")
@patch("scrapers.scrap_4_get_comments.get_engine")
def test_update_stage_success(mock_engine, mock_session_class):
    scraper = CommentsScraper()
    scraper._article_id = 1

    mock_obj = MagicMock()
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.one.return_value = mock_obj
    mock_session_class.return_value.__enter__.return_value = mock_session

    scraper._update_stage()

    assert mock_obj.stage == 3
    mock_session.commit.assert_called_once()

# -----------------------
# Test: entry_point (all steps)
# -----------------------

@patch("utils.scraper.ServiceBusClient")  # Prevent Azure call
@patch.object(CommentsScraper, "abandon_message")
@patch.object(CommentsScraper, "log_scraper_error")
@patch.object(CommentsScraper, "_update_stage")
@patch.object(CommentsScraper, "_add_new_comments")
@patch.object(CommentsScraper, "_get_articles_comments")
@patch.object(CommentsScraper, "_get_article_uid")
def test_entry_point(
    mock_get_uid,
    mock_get_comments,
    mock_add_comments,
    mock_update_stage,
    mock_log_error,
    mock_abandon_message,
    mock_sb_client
):
    scraper = CommentsScraper()
    scraper._service_bus_queue_source = "queue_comments"  # to avoid init errors

    # Run entry point with article_id so queue is not hit
    CommentsScraper.entry_point(article_id=456)

    mock_get_uid.assert_called_once()
    mock_get_comments.assert_called_once()
    mock_add_comments.assert_called_once()
    mock_update_stage.assert_called_once()
    mock_abandon_message.assert_not_called()
    mock_log_error.assert_not_called()
