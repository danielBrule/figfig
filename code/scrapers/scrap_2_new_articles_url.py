import requests
import xml.etree.ElementTree as ET
from enum import Enum
import dateutil
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import session, engine
from db.models import ArticlesURLs, SitemapURLs
from utils.log import logger


class Newspaper(Enum):
    Lefigaro = 1


NAMESPACE = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

LIST_COLUMNS_URLS = ["url"]


class ArticlesURLsNew:
    def __init__(self, newspaper: Newspaper, sitemap_urls_id: int):
        logger.info("ArticlesURLs.__init__")
        self._newspaper = newspaper
        self._sitemap_urls_id = sitemap_urls_id
        self._orl_articles = []
        self._l_all_articles_urls = []
        self._l_new_articles_urls = []

        self._url_articles_xml = None

    def _get_sitemap_url(self):
        stmt = select(SitemapURLs.url).where(SitemapURLs.id == self._sitemap_urls_id)
        self._url_articles_xml = session.execute(stmt).scalar_one_or_none()

    def _get_articles_url(self):
        logger.info("ArticlesURLs._get_articles_url")
        articles_xml = requests.get(self._url_articles_xml)
        root = ET.fromstring(articles_xml.text)
        for sitemap in root.findall("ns:url", NAMESPACE):
            loc = sitemap.find("ns:loc", NAMESPACE).text
            lastmod = sitemap.find("ns:lastmod", NAMESPACE).text
            lastmod = dateutil.parser.isoparse(lastmod)
            priority = sitemap.find("ns:priority", NAMESPACE).text
            self._orl_articles.append(ArticlesURLs(url=loc,
                                                   last_modification=lastmod,
                                                   to_process=True,
                                                   priority=priority,
                                                   source_id=self._sitemap_urls_id,))
            self._l_all_articles_urls.append(loc)
        logger.info(f"\t{len(self._orl_articles)} articles' urls gathered")

    def _remove_urls_already_in_db(self):
        logger.info("ArticlesURLs._remove_existing_sitemap")
        stmt = select(ArticlesURLs.url).where(ArticlesURLs.url.in_(self._l_all_articles_urls))

        with Session(engine) as session:
            existing_values = {row[0] for row in session.execute(stmt)}

        # values NOT in the table
        self._l_new_articles_urls = [val for val in self._l_all_articles_urls if val not in existing_values]

        self._orl_articles = [article for article in self._orl_articles
                              if article.url in self._l_new_articles_urls]

    def _add_new_urls(self):
        logger.info("ArticlesURLs._add_new_urls")
        session.add_all(self._orl_articles)
        session.commit()

        logger.info(f"{len(self._orl_articles)} new articles' URLs inserted into the database.")

    def _update_sitemap_url(self):
        logger.info("ArticlesURLs._update_sitemap_url")
        try:
            obj = (session.query(SitemapURLs)
                        .filter(SitemapURLs.id == self._sitemap_urls_id)
                        .one())
            obj.to_process = False
            session.commit()#
        except Exception as ex:
            logger.error(f"ArticlesURLs._update_sitemap_url - Commit failed: {e}")
            session.rollback()
            session.query(ArticlesURLs).filter(ArticlesURLs.url.in_(self._l_new_articles_urls)).delete(synchronize_session=False)
            session.commit()
            raise ex 

    def entry_point(self):
        logger.info("ArticlesURLs.entry_point")
        self._get_sitemap_url()
        self._remove_urls_already_in_db()
        if len(self._l_new_articles_urls) > 0:
            self._get_articles_url()
            self._add_new_urls()
            self._update_sitemap_url()
        else: 
            logger.warning(f"ArticlesURLs._update_sitemap_url '{self._url_articles_xml}' has no articles")

if __name__ == "__main__":
    parser = ArticlesURLsNew(newspaper=Newspaper.Lefigaro, sitemap_urls_id=12)
    parser.entry_point()
