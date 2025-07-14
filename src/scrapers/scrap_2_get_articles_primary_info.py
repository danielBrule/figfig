import requests
import xml.etree.ElementTree as ET
from enum import Enum
import dateutil
from sqlalchemy import select
from sqlalchemy.orm import Session
import os
from db.database import get_engine
from db.models import ArticlesURLs, SitemapURLs
from utils.log import logger
from utils.constants import ArticleStageEnum, NAMESPACE
from utils.scraper import Scraper
from utils.constants import ServiceQueue


class ArticlesPrimaryInfoScraper(Scraper):
    def __init__(self):
        logger.info("class ArticlesPrimaryInfoScraper.__init__")
        super().__init__()
        self._stage = "ArticlesPrimaryInfoScraper"
        self._sitemap_urls_id = None
        self._l_all_articles = []
        self._l_all_articles_urls = []

        self._l_new_articles = []
        self._l_new_articles_urls = []

        self._url_articles_xml = None
        self._service_bus_queue_source = ServiceQueue.articles_primary_info.value
        self._service_bus_queue_destination = ServiceQueue.articles_secondary_info.value

    def _get_sitemap_url(self):
        logger.info("ArticlesPrimaryInfoScraper._get_sitemap_url")
        stmt = select(SitemapURLs.url).where(SitemapURLs.id == self._sitemap_urls_id)
        with Session(get_engine()) as session:
            self._url_articles_xml = session.execute(stmt).scalar_one_or_none()
            logger.info(f"\tURL: {self._url_articles_xml}")

    def _get_articles_url(self):
        logger.info("ArticlesPrimaryInfoScraper._get_articles_url")
        articles_xml = requests.get(self._url_articles_xml)
        root = ET.fromstring(articles_xml.text)
        for sitemap in root.findall("ns:url", NAMESPACE):
            loc = sitemap.find("ns:loc", NAMESPACE).text
            lastmod = sitemap.find("ns:lastmod", NAMESPACE).text
            lastmod = dateutil.parser.isoparse(lastmod)
            priority = sitemap.find("ns:priority", NAMESPACE).text
            self._l_all_articles.append(
                ArticlesURLs(
                    url=loc,
                    last_modification=lastmod,
                    stage=ArticleStageEnum.UrlGathered.value,
                    priority=priority,
                    source_id=self._sitemap_urls_id,
                    insert_date=self._now,
                )
            )
            self._l_all_articles_urls.append(loc)
        logger.info(f"\t{len(self._l_all_articles)} articles' urls gathered")

    def _remove_urls_already_in_db(self):
        logger.info("ArticlesPrimaryInfoScraper._remove_urls_already_in_db")
        stmt = select(ArticlesURLs.url).where(
            ArticlesURLs.url.in_(self._l_all_articles_urls)
        )

        with Session(get_engine()) as session:
            existing_values = {row[0] for row in session.execute(stmt)}

        # values NOT in the table
        self._l_new_articles_urls = [
            val for val in self._l_all_articles_urls if val not in existing_values
        ]
        logger.info(
            f"\t{len(self._l_new_articles_urls)} new articles' urls to be inserted into the database."
        )

        self._l_new_articles = [
            article
            for article in self._l_all_articles
            if article.url in self._l_new_articles_urls
        ]
        logger.info(
            f"\t{len(self._l_new_articles)} articles' will be inserted into the database."
        )
        assert len(self._l_new_articles) == len(self._l_new_articles_urls), (
            "The number of articles to be inserted does not match the number of new URLs."
        )

    def _add_new_urls(self):
        logger.info("ArticlesPrimaryInfoScraper._add_new_urls")
        with Session(get_engine(), expire_on_commit=False) as session:
            session.add_all(self._l_new_articles)
            session.commit()

        logger.info(
            f"{len(self._l_new_articles)} new articles' URLs inserted into the database."
        )

    def _update_sitemap_url(self):
        logger.info("ArticlesPrimaryInfoScraper._update_sitemap_url")
        try:
            with Session(get_engine()) as session:
                obj = (
                    session.query(SitemapURLs)
                    .filter(SitemapURLs.id == self._sitemap_urls_id)
                    .one()
                )
                obj.to_process = False
                session.commit()  #
        except Exception as ex:
            logger.error(f"ArticlesURLs._update_sitemap_url - Commit failed: {ex}")
            with Session(get_engine()) as session:
                session.rollback()
                session.query(ArticlesURLs).filter(
                    ArticlesURLs.url.in_(self._l_new_articles_urls)
                ).delete(synchronize_session=False)
                session.commit()
            raise ex

    def _send_message_to_service_bus(self):
        logger.info("ArticlesPrimaryInfoScraper._send_message_to_service_bus")
        new_ids = [str(u.id) for u in self._l_all_articles]
        self.send_message(messages=new_ids)

    def _error_recovery(self) -> None:
        # todo
        pass

    @staticmethod
    def entry_point(sitetmap_urls_id: int = None):
        logger.info("ArticlesPrimaryInfoScraper.entry_point")

        scraper = ArticlesPrimaryInfoScraper()

        if sitetmap_urls_id is None:
            scraper.get_one_message()
            scraper._sitemap_urls_id = scraper._servicebus_source_message
            if scraper._servicebus_source_message is None:
                logger.info("No messages to process in the queue.")
                return
            else:
                scraper._sitemap_urls_id = int(str(scraper._sitemap_urls_id))
        else:
            scraper._sitemap_urls_id = sitetmap_urls_id

        if scraper._sitemap_urls_id is not None:
            logger.info(f"Processing: {scraper._sitemap_urls_id}")
            try:
                scraper._get_sitemap_url()
                scraper._get_articles_url()
                scraper._remove_urls_already_in_db()
                if len(scraper._l_new_articles_urls) > 0:
                    scraper._add_new_urls()
                    scraper._update_sitemap_url()
                else:
                    logger.warning(
                        f"ArticlesPrimaryInfoScraper._update_sitemap_url '{scraper._url_articles_xml}' has no new articles"
                    )
                scraper._send_message_to_service_bus()
                scraper.complete_message()
            except Exception as e:
                logger.error(f"Error: {e}")
                scraper.abandon_message()
                scraper.log_scraper_error(id=scraper._sitemap_urls_id, error=e)
        logger.info("ArticlesPrimaryInfoScraper completed successfully.")


if __name__ == "__main__":
    if os.getenv("ON_AZURE") is not None and os.getenv("ON_AZURE").lower() == "true":
        ArticlesPrimaryInfoScraper.entry_point()
    else:
        ArticlesPrimaryInfoScraper.entry_point(sitetmap_urls_id=12)
