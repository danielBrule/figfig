import requests
import xml.etree.ElementTree as ET
import datetime
import dateutil
import os
from sqlalchemy import select
from dateutil.tz import tzoffset
from sqlalchemy.orm import Session

from db.database import get_engine
from db.models import SitemapURLs
from utils.constants import NewspaperEnum, NAMESPACE
from utils.log import logger
from utils.scraper import Scraper
from utils.constants import ServiceQueue

URL_ARTICLES = "https://sitemaps.lefigaro.fr/lefigaro.fr/articles.xml"


class DailyURLsScraper(Scraper):
    def __init__(self, newspaper: NewspaperEnum):
        logger.info("DailyURLsScraper.__init__")
        super().__init__()
        self._stage = "DailyURLsScraper"
        self._newspaper = newspaper
        self._d_urls_sitemap = {}
        self._l_urls_sitemap_new = []
        self._l_urls_sitemap_updated = []
        self._service_bus_queue_destination = ServiceQueue.articles_primary_info.value

    def _get_daily_urls(self):
        logger.info("DailyURLsScraper._get_daily_urls")
        site_map_actu_xml = requests.get(URL_ARTICLES)
        root = ET.fromstring(site_map_actu_xml.text)
        for sitemap in root.findall("ns:sitemap", NAMESPACE):
            loc = sitemap.find("ns:loc", NAMESPACE).text
            lastmod = sitemap.find("ns:lastmod", NAMESPACE).text
            lastmod = dateutil.parser.isoparse(lastmod)
            is_old = (self._now - lastmod) > datetime.timedelta(days=7)
            if is_old:
                self._d_urls_sitemap[loc] = lastmod
        logger.info(f"\t{len(self._d_urls_sitemap)} urls gathered")

    def _get_daily_urls_to_process(self):
        logger.info("DailyURLsScraper._remove_existing_sitemap")
        stmt = select(SitemapURLs)
        with Session(get_engine()) as session:
            existing_urls = session.scalars(stmt).all()

        logger.info(f"\t{len(existing_urls)} urls already in the db")

        dict_existing_urls = {}
        for existing_url in existing_urls:
            dict_existing_urls[existing_url.url] = existing_url.last_modification

        for url, updated_date in self._d_urls_sitemap.items():
            if url not in dict_existing_urls:
                self._l_urls_sitemap_new.append(
                    SitemapURLs(
                        url=url,
                        last_modification=updated_date,
                        to_process=True,
                        newspaper_id=self._newspaper.value,
                        insert_date=self._now,
                    )
                )
            elif dict_existing_urls[url].replace(
                tzinfo=tzoffset(None, 7200)
            ) != updated_date.replace(tzinfo=tzoffset(None, 7200)):
                self._l_urls_sitemap_updated.append(
                    SitemapURLs(
                        url=url,
                        last_modification=updated_date,
                        to_process=True,
                        newspaper_id=self._newspaper.value,
                        insert_date=self._now,
                    )
                )

    def _add_new_urls(self):
        logger.info("DailyURLsScraper._add_new_urls")
        if os.getenv("APP_ENV") == "dev":
            self._l_urls_sitemap_new = self._l_urls_sitemap_new[:10]

        with Session(get_engine()) as session:
            session.add_all(self._l_urls_sitemap_new)
            session.commit()

        logger.info(
            f"\t{len(self._l_urls_sitemap_new)} new URLs inserted into the database."
        )

    # def _update_urls(self):
    #     logger.info("DailyURLsScraper._update_urls")
    #     with Session(get_engine()) as session:
    #         session.bulk_update_mappings(SitemapURLs, self._l_urls_sitemap_updated)
    #         session.commit()

    #     logger.info(f"{len(self._l_urls_sitemap_updated)} new URLs updated into the database.")

    @staticmethod
    def entry_point():
        parser = DailyURLsScraper(newspaper=NewspaperEnum.Lefigaro)
        try: 

            logger.info("DailyURLsScraper.entry_point")
            parser._get_daily_urls()
            parser._get_daily_urls_to_process()
            parser._add_new_urls()
        except Exception as e:
            logger.error(f"Error: {e}")
            parser.log_scraper_error(
                id=None,
                error=e
            )
        # self._update_urls()


if __name__ == "__main__":
        DailyURLsScraper.entry_point()
