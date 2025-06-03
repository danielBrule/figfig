import requests
import xml.etree.ElementTree as ET
from enum import Enum
import pandas as pd
import datetime 
import dateutil
from db.database import Session 

class Newspaper(Enum):
    Lefigaro = 1
    

URL_ARTICLES = "https://sitemaps.lefigaro.fr/lefigaro.fr/articles.xml"
NAMESPACE = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

LIST_COLUMNS_URLS = ["url"]

class SitemapArticles:
    def __init__(self, newspaper: Newspaper):
        self._newspaper = newspaper
        self._df = None
        self._df_url_sitemap = None
        
        self._df = pd.DataFrame(columns=LIST_COLUMNS_URLS)

        self._now = datetime.datetime.now(datetime.timezone.utc)


    def _download_daily_xml(self):
        site_map_actu_xml = requests.get(URL_ARTICLES)
        root = ET.fromstring(site_map_actu_xml.text)
        url_sitemap = []
        for sitemap in root.findall('ns:sitemap', NAMESPACE):
            loc = sitemap.find('ns:loc', NAMESPACE).text
            lastmod = sitemap.find('ns:lastmod', NAMESPACE).text
            lastmod = dateutil.parser.isoparse(lastmod)
            is_recent = (self._now - lastmod) < datetime.timedelta(days=2)
            url_sitemap.append({'loc': loc, 'lastmod': lastmod, "is_recent": is_recent})
        
        self._df_url_sitemap = pd.DataFrame(url_sitemap)
        
    def _get_all_articles(self):
        

    def entry_point(self): 
        self._download_daily_xml()
        self._get_all_articles()

parser = SitemapArticles(newspaper=Newspaper.Lefigaro)
parser.entry_point()
