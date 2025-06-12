import pytest
from unittest.mock import patch, MagicMock
import datetime

from utils.constants import ArticleStageEnum
from scrapers.scrap_2_get_articles_primary_info import ArticlesPrimaryInfoScraper  
from db.models import SitemapURLs, ArticlesURLs

@pytest.fixture(autouse=True)
def mock_key_vault_secret():
    with patch("azure.keyvault.secrets.SecretClient.get_secret") as mock_get_secret:
        mock_get_secret.return_value.value = "fake-password"
        yield


TEST_SITEMAP_URL = "https://example.com/sitemap.xml"
FAKE_ARTICLE_XML = """
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/article-1</loc>
    <lastmod>2023-06-01T12:00:00+00:00</lastmod>
    <priority>0.8</priority>
  </url>
</urlset>
"""

# ----------------------------
# _get_sitemap_url
# ----------------------------
@patch("scrapers.scrap_2_get_articles_primary_info.Session")
def test_get_sitemap_url(mock_session_class):
    scraper = ArticlesPrimaryInfoScraper(sitemap_urls_id=1)
    mock_session = MagicMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = TEST_SITEMAP_URL
    mock_session_class.return_value.__enter__.return_value = mock_session

    scraper._get_sitemap_url()

    assert scraper._url_articles_xml == TEST_SITEMAP_URL
    mock_session.execute.assert_called()

# ----------------------------
# _get_articles_url
# ----------------------------
@patch("scrapers.scrap_2_get_articles_primary_info.requests.get")
def test_get_articles_url_parses_correctly(mock_get):
    scraper = ArticlesPrimaryInfoScraper(sitemap_urls_id=1)
    scraper._url_articles_xml = TEST_SITEMAP_URL

    mock_response = MagicMock()
    mock_response.text = FAKE_ARTICLE_XML
    mock_get.return_value = mock_response

    scraper._get_articles_url()

    assert len(scraper._orl_articles) == 1
    assert scraper._orl_articles[0].url == "https://example.com/article-1"
    assert scraper._orl_articles[0].priority == "0.8"
    assert scraper._orl_articles[0].stage == ArticleStageEnum.UrlGathered.value

# ----------------------------
# _remove_urls_already_in_db
# ----------------------------
@patch("scrapers.scrap_2_get_articles_primary_info.Session")
def test_remove_urls_already_in_db(mock_session_class):
    scraper = ArticlesPrimaryInfoScraper(sitemap_urls_id=1)
    scraper._l_all_articles_urls = ["https://example.com/article-1", "https://example.com/article-2"]
    scraper._orl_articles = [
        ArticlesURLs(url="https://example.com/article-1"),
        ArticlesURLs(url="https://example.com/article-2"),
    ]

    mock_session = MagicMock()
    mock_session.execute.return_value = [("https://example.com/article-1",)]
    mock_session_class.return_value.__enter__.return_value = mock_session

    scraper._remove_urls_already_in_db()

    assert scraper._l_new_articles_urls == ["https://example.com/article-2"]
    assert len(scraper._orl_articles) == 1
    assert scraper._orl_articles[0].url == "https://example.com/article-2"

# ----------------------------
# _add_new_urls
# ----------------------------
@patch("scrapers.scrap_2_get_articles_primary_info.Session")
def test_add_new_urls_commits(mock_session_class):
    scraper = ArticlesPrimaryInfoScraper(sitemap_urls_id=1)
    scraper._orl_articles = [ArticlesURLs(url="https://example.com/article-1")]

    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session

    scraper._add_new_urls()

    mock_session.add_all.assert_called_once_with(scraper._orl_articles)
    mock_session.commit.assert_called_once()

# ----------------------------
# _update_sitemap_url
# ----------------------------
@patch("scrapers.scrap_2_get_articles_primary_info.Session")
def test_update_sitemap_url_success(mock_session_class):
    scraper = ArticlesPrimaryInfoScraper(sitemap_urls_id=1)

    mock_session = MagicMock()
    obj = MagicMock()
    mock_session.query.return_value.filter.return_value.one.return_value = obj
    mock_session_class.return_value.__enter__.return_value = mock_session

    scraper._update_sitemap_url()

    assert obj.to_process is False
    mock_session.commit.assert_called_once()

@patch("scrapers.scrap_2_get_articles_primary_info.Session")
def test_update_sitemap_url_failure(mock_session_class):
    scraper = ArticlesPrimaryInfoScraper(sitemap_urls_id=1)
    scraper._l_new_articles_urls = ["https://example.com/article-1"]

    # First context: fails on .one()
    mock_session_main_ctx = MagicMock()
    mock_session_main_ctx.query.return_value.filter.return_value.one.side_effect = Exception("DB fail")

    mock_session_main = MagicMock()
    mock_session_main.__enter__.return_value = mock_session_main_ctx

    # Second context: handles rollback and delete
    mock_session_recovery_ctx = MagicMock()
    mock_session_recovery = MagicMock()
    mock_session_recovery.__enter__.return_value = mock_session_recovery_ctx

    mock_session_class.side_effect = [mock_session_main, mock_session_recovery]

    with pytest.raises(Exception, match="DB fail"):
        scraper._update_sitemap_url()

    mock_session_recovery_ctx.rollback.assert_called_once()
    mock_session_recovery_ctx.commit.assert_called_once()


# ----------------------------
# entry_point
# ----------------------------
@patch.object(ArticlesPrimaryInfoScraper, "_get_sitemap_url")
@patch.object(ArticlesPrimaryInfoScraper, "_get_articles_url")
@patch.object(ArticlesPrimaryInfoScraper, "_remove_urls_already_in_db")
@patch.object(ArticlesPrimaryInfoScraper, "_add_new_urls")
@patch.object(ArticlesPrimaryInfoScraper, "_update_sitemap_url")
def test_entry_point_with_new_articles(
    mock_update, mock_add, mock_remove, mock_get_articles, mock_get_sitemap
):
    scraper = ArticlesPrimaryInfoScraper(sitemap_urls_id=1)
    scraper._l_new_articles_urls = ["https://example.com/article-1"]

    scraper.entry_point()

    mock_get_sitemap.assert_called_once()
    mock_get_articles.assert_called_once()
    mock_remove.assert_called_once()
    mock_add.assert_called_once()
    mock_update.assert_called_once()

@patch.object(ArticlesPrimaryInfoScraper, "_get_sitemap_url")
@patch.object(ArticlesPrimaryInfoScraper, "_get_articles_url")
@patch.object(ArticlesPrimaryInfoScraper, "_remove_urls_already_in_db")
@patch.object(ArticlesPrimaryInfoScraper, "_add_new_urls")
@patch.object(ArticlesPrimaryInfoScraper, "_update_sitemap_url")
def test_entry_point_with_no_new_articles(
    mock_update, mock_add, mock_remove, mock_get_articles, mock_get_sitemap
):
    scraper = ArticlesPrimaryInfoScraper(sitemap_urls_id=1)
    scraper._l_new_articles_urls = []

    scraper.entry_point()

    mock_get_sitemap.assert_called_once()
    mock_get_articles.assert_called_once()
    mock_remove.assert_called_once()
    mock_add.assert_not_called()
    mock_update.assert_not_called()
