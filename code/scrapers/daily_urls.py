import requests
import xml.etree.ElementTree as ET
from enum import Enum
import datetime 
import dateutil
from sqlalchemy import select
from dateutil.tz import tzoffset

from db.database import session
from db.models import SitemapURLs
from utils.log import logger

class Newspaper(Enum):
    Lefigaro = 1
    

URL_ARTICLES = "https://sitemaps.lefigaro.fr/lefigaro.fr/articles.xml"
NAMESPACE = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

LIST_COLUMNS_URLS = ["url"]

class DailyURLs:
    def __init__(self, newspaper: Newspaper):
        logger.info("SitemapArticles.__init__")
        self._newspaper = newspaper
        self._d_urls_sitemap = {}    
        self._l_urls_sitemap_new = []
        self._l_urls_sitemap_updated = []
        self._now = datetime.datetime.now(datetime.timezone.utc)


    def _get_daily_urls(self):
        logger.info("SitemapArticles._download_daily_xml")
        site_map_actu_xml = requests.get(URL_ARTICLES)
        root = ET.fromstring(site_map_actu_xml.text)
        for sitemap in root.findall('ns:sitemap', NAMESPACE):
            loc = sitemap.find('ns:loc', NAMESPACE).text
            lastmod = sitemap.find('ns:lastmod', NAMESPACE).text
            lastmod = dateutil.parser.isoparse(lastmod)
            is_old = (self._now - lastmod) > datetime.timedelta(days=7)
            if is_old:
                self._d_urls_sitemap[loc] = lastmod
        logger.info(f"\t{len(self._d_urls_sitemap)} urls gathered")
                
    def _get_daily_urls_to_process(self):
        logger.info("SitemapArticles._remove_existing_sitemap")
        stmt = select(SitemapURLs)
        
        existing_urls = session.scalars(stmt).all()
        
        logger.info(f"\t{len(existing_urls)} urls already in the db")

        dict_existing_urls = {}
        for existing_url in existing_urls:
             dict_existing_urls[existing_url.url] = existing_url.last_modification
            
        for url, updated_date in self._d_urls_sitemap.items(): 
            if url not in dict_existing_urls:
                self._l_urls_sitemap_new.append(SitemapURLs(url= url, last_modification=updated_date, to_process=True))
            elif dict_existing_urls[url].replace(tzinfo=tzoffset(None, 7200)) != updated_date.replace(tzinfo=tzoffset(None, 7200)):
                self._l_urls_sitemap_updated.append(SitemapURLs(url= url, last_modification=updated_date, to_process=True))
        
    def _add_new_urls(self):
        logger.info("SitemapArticles._add_new_urls")
        session.add_all(self._l_urls_sitemap_new)
        session.commit()

        logger.info(f"{len(self._l_urls_sitemap_new)} new URLs inserted into the database.")
        
    def _update_urls(self):
        logger.info("SitemapArticles._update_urls")
        session.bulk_update_mappings(self._l_urls_sitemap_updated)
        session.commit()

        logger.info(f"{len(self._l_urls_sitemap_updated)} new URLs updated into the database.")
        
    def entry_point(self): 
        logger.info("SitemapArticles.entry_point")
        self._get_daily_urls()
        self._get_daily_urls_to_process()
        self._add_new_urls()

parser = DailyURLs(newspaper=Newspaper.Lefigaro)
parser.entry_point()
