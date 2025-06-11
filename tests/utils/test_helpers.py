import pytest
from unittest.mock import patch, MagicMock
import datetime
from   scrapers.scrap_1_get_daily_urls import DailyURLsScraper
from utils.constants import NewspaperEnum

# Sample XML response for _get_daily_urls
SAMPLE_XML = """
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>http://example.com/sitemap1.xml</loc>
    <lastmod>2025-06-01T00:00:00+00:00</lastmod>
  </sitemap>
  <sitemap>
    <loc>http://example.com/sitemap2.xml</loc>
    <lastmod>2023-01-01T00:00:00+00:00</lastmod>
  </sitemap>
</urlset>
"""

@pytest.fixture
def scraper():
    return DailyURLsScraper(newspaper=NewspaperEnum.Lefigaro)

@patch("yourmodule.requests.get")
def test_get_daily_urls(mock_get, scraper):
    mock_get.return_value.text = SAMPLE_XML
    
    # Freeze time to a fixed date to control date calculations
    scraper._now = datetime.datetime(2025, 6, 8, tzinfo=datetime.timezone.utc)
    
    scraper._get_daily_urls()
    
    # Only the sitemap with lastmod older than 7 days from _now should be included
    assert "http://example.com/sitemap2.xml" in scraper._d_urls_sitemap
    assert "http://example.com/sitemap1.xml" not in scraper._d_urls_sitemap

@patch("yourmodule.Session")
def test_get_daily_urls_to_process(mock_session_class, scraper):
    # Prepare scraper._d_urls_sitemap to simulate URLs from _get_daily_urls
    old_date = datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc)
    new_date = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)
    scraper._d_urls_sitemap = {
        "http://example.com/new_url.xml": new_date,
        "http://example.com/existing_url.xml": new_date,
        "http://example.com/updated_url.xml": new_date,
    }
    
    # Mock existing URLs in DB
    existing_url_obj = MagicMock()
    existing_url_obj.url = "http://example.com/existing_url.xml"
    existing_url_obj.last_modification = new_date
    
    updated_url_obj = MagicMock()
    # Last modification date different from scraper._d_urls_sitemap date
    updated_url_obj.url = "http://example.com/updated_url.xml"
    updated_url_obj.last_modification = old_date
    
    # Mock the session.scalars().all() call to return existing URLs
    mock_session = MagicMock()
    mock_session.scalars.return_value.all.return_value = [existing_url_obj, updated_url_obj]
    mock_session_class.return_value.__enter__.return_value = mock_session
    
    scraper._newspaper = NewspaperEnum.Lefigaro
    
    scraper._get_daily_urls_to_process()
    
    # New URL should be in _l_urls_sitemap_new
    new_urls = [item.url for item in scraper._l_urls_sitemap_new]
