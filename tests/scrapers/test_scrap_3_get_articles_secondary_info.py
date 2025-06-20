import pytest
from unittest.mock import patch, MagicMock

from scrapers.scrap_3_get_articles_secondary_info import ArticlesSecondaryInfoScraper
from utils.constants import ArticleStageEnum


@pytest.fixture(autouse=True)
def mock_key_vault_secret():
    with patch("azure.keyvault.secrets.SecretClient.get_secret") as mock_get_secret:
        mock_get_secret.return_value.value = "fake-password"
        yield


# --- Test _update_stage: success case ---
@patch("scrapers.scrap_3_get_articles_secondary_info.Session")
def test_update_stage_success(mock_session_class):
    scraper = ArticlesSecondaryInfoScraper(article_id=1)

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
    scraper = ArticlesSecondaryInfoScraper(article_id=1)

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
@patch.object(ArticlesSecondaryInfoScraper, "_get_article_url")
@patch.object(ArticlesSecondaryInfoScraper, "_get_articles_info")
@patch.object(ArticlesSecondaryInfoScraper, "_add_new_keywords")
@patch.object(ArticlesSecondaryInfoScraper, "_get_keywords_id")
@patch.object(ArticlesSecondaryInfoScraper, "_add_articles")
@patch.object(ArticlesSecondaryInfoScraper, "add_keywords")
@patch.object(ArticlesSecondaryInfoScraper, "_update_stage")
def test_entry_point(
    mock_update_stage,
    mock_add_keywords,
    mock_add_articles,
    mock_get_keywords_id,
    mock_add_new_keywords,
    mock_get_articles_info,
    mock_get_article_url
):
    scraper = ArticlesSecondaryInfoScraper(article_id=1)

    scraper.entry_point()

    mock_get_article_url.assert_called_once()
    mock_get_articles_info.assert_called_once()
    mock_add_new_keywords.assert_called_once()
    mock_get_keywords_id.assert_called_once()
    mock_add_articles.assert_called_once()
    mock_add_keywords.assert_called_once()
    mock_update_stage.assert_called_once()
