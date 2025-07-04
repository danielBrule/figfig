import pytest
from unittest.mock import patch, MagicMock

from scrapers.scrap_3_get_articles_secondary_info import ArticlesSecondaryInfoScraper
from utils.constants import ArticleStageEnum

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


# --- Test _update_stage: success case ---
@patch("scrapers.scrap_3_get_articles_secondary_info.Session")
def test_update_stage_success(mock_session_class):
    scraper = ArticlesSecondaryInfoScraper()
    scraper.article_id = 1

    mock_session = MagicMock()
    mock_query = MagicMock()
    mock_obj = MagicMock()
    mock_query.filter.return_value.one.return_value = mock_obj
    mock_session.query.return_value = mock_query
    mock_session_class.return_value.__enter__.return_value = mock_session

    scraper._update_stage()

    assert mock_obj.stage == ArticleStageEnum.ArticleGathered.value
    mock_session.commit.assert_called_once()

# --- Test _update_stage: failure case ---
@patch("scrapers.scrap_3_get_articles_secondary_info.Session")
def test_update_stage_failure(mock_session_class):
    scraper = ArticlesSecondaryInfoScraper()
    scraper.article_id = 1

    # First session raises
    mock_session_main = MagicMock()
    mock_session_main.query.return_value.filter.return_value.one.side_effect = Exception("DB fail")
    mock_session_main.__enter__.return_value = mock_session_main

    # Recovery sessions
    mock_session_second = MagicMock()
    mock_session_second.__enter__.return_value = mock_session_second

    mock_session_third = MagicMock()
    mock_session_third.__enter__.return_value = mock_session_third

    mock_session_class.side_effect = [mock_session_main, mock_session_second, mock_session_third]

    with pytest.raises(Exception, match="DB fail"):
        scraper._update_stage()

    mock_session_second.rollback.assert_called_once()
    mock_session_second.commit.assert_called_once()
    mock_session_third.rollback.assert_called_once()
    mock_session_third.commit.assert_called_once()

# --- Test entry_point (fully mocked) ---
@patch("utils.scraper.ServiceBusClient")  # prevent Azure call
@patch.object(ArticlesSecondaryInfoScraper, "abandon_message")
@patch.object(ArticlesSecondaryInfoScraper, "log_scraper_error")
@patch.object(ArticlesSecondaryInfoScraper, "_update_stage")
@patch.object(ArticlesSecondaryInfoScraper, "add_keywords")
@patch.object(ArticlesSecondaryInfoScraper, "_add_articles")
@patch.object(ArticlesSecondaryInfoScraper, "_get_keywords_id")
@patch.object(ArticlesSecondaryInfoScraper, "_add_new_keywords")
@patch.object(ArticlesSecondaryInfoScraper, "_get_articles_info")
@patch.object(ArticlesSecondaryInfoScraper, "_get_article_url")
def test_entry_point(
    mock_get_url,
    mock_get_info,
    mock_add_new_keywords,
    mock_get_keyword_ids,
    mock_add_articles,
    mock_add_keywords,
    mock_update_stage,
    mock_log_error,
    mock_abandon_message,
    mock_sb_client
):
    scraper = ArticlesSecondaryInfoScraper()
    scraper._service_bus_queue_destination = "queue_comments"  # set explicitly to prevent ValueError
    scraper.entry_point(article_id=123)

    mock_get_url.assert_called_once()
    mock_get_info.assert_called_once()
    mock_add_new_keywords.assert_called_once()
    mock_get_keyword_ids.assert_called_once()
    mock_add_articles.assert_called_once()
    mock_add_keywords.assert_called_once()
    mock_update_stage.assert_called_once()
    mock_abandon_message.assert_not_called()
    mock_log_error.assert_not_called()