
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import Session

import dateutil
from db.database import get_engine
from db.models import ArticlesURLs, Articles, Keywords, ArticleKeywords
from utils.log import logger
from utils.constants import ArticleStageEnum
from utils.helpers import simple_get


class ArticlesSecondaryInfoScraper:
    def __init__(self, article_id: int):
        logger.info("ArticlesSecondaryInfoScraper.__init__")
        self._article_id = article_id
        self._url_articles = None
        self._articles = None
        
        self._title = None
        self._publication_date =None
        self._last_modification_date = None
        self._l_keywords = None
        self._l_keywords_id = None
        self._description =None
        self._uid = None

    def _get_article_url(self):
        logger.info("ArticlesSecondaryInfoScraper._get_article_url")
        stmt = select(ArticlesURLs.url).where(ArticlesURLs.id == self._article_id)
        with Session(get_engine()) as session:
            self._url_articles = session.execute(stmt).scalar_one_or_none()
        logger.info(f"\tURL: {self._url_articles}")
        
        
    def _get_articles_info(self):
        logger.info("ArticlesSecondaryInfoScraper._get_articles_info")
        raw_html = simple_get(self._url_articles)
        html = BeautifulSoup(raw_html, 'html.parser')
        self._title = html.find(name="title").text.strip()
        self._publication_date = html.find(name="meta", attrs={"property": "article:published_time"}).attrs["content"].split(",")
        self._publication_date = dateutil.parser.isoparse(self._publication_date[0])
        
        self._last_modification_date = html.find(name="meta", attrs={"property": "article:modified_time"}).attrs["content"].split(",")
        self._last_modification_date = dateutil.parser.isoparse(self._last_modification_date[0])

        
        self._l_keywords = html.find(name="meta", attrs={"property": "article:tag"}).attrs["content"].split(",")
        self._description = html.find(name="meta", attrs={"name": "description"}).attrs["content"].strip()
        
        self._uid = html.find(name="div", attrs={"class": "fig-content-body"}).attrs["data-id"]

    def _add_new_keywords(self):
        logger.info("ArticlesSecondaryInfoScraper._add_keywords")
        stmt = select(Keywords.full_keyword).where(Keywords.full_keyword.in_(self._l_keywords))

        with Session(get_engine()) as session:
            existing_keywords = {row[0] for row in session.execute(stmt)}

        # values NOT in the table
        l_new_keywords = [Keywords(full_keyword=keyword) for keyword in self._l_keywords if keyword not in existing_keywords]
        logger.info (f"\t{len(l_new_keywords)} new keywords have been identified")
        
        if len(l_new_keywords) > 0:
            with Session(get_engine()) as session:
                session.add_all(l_new_keywords)
                session.commit()

    def _get_keywords_id(self):
        logger.info("ArticlesSecondaryInfoScraper._get_keywords_id")
        stmt = select(Keywords.id).where(Keywords.full_keyword.in_(self._l_keywords))

        with Session(get_engine()) as session:
            self._l_keywords_id = {row[0] for row in session.execute(stmt)}


    def _add_articles(self):
        logger.info("ArticlesSecondaryInfoScraper._add_articles")
        self._articles= Articles(id=self._article_id,
                                 title=self._title,
                                 publication_date=self._publication_date,
                                 last_modification_date=self._last_modification_date,
                                 description = self._description,
                                 uid = self._uid)

        with Session(get_engine()) as session:
            session.add(self._articles)
            session.commit()
        logger.info(f"\tarticle has been added")


    def add_keywords(self):
        logger.info("ArticlesSecondaryInfoScraper.add_keywords")
        
        l_orl_article_keywords = [ArticleKeywords(article_id=self._article_id, keyword_id=keyword_id) 
                                  for keyword_id in self._l_keywords_id]
        with Session(get_engine()) as session:
            session.add_all(l_orl_article_keywords)
            session.commit()
        logger.info(f"\t{len(l_orl_article_keywords)} keywords have been added")


    def _update_stage(self):
        logger.info("ArticlesSecondaryInfoScraper._update_stage")
        try:
            with Session(get_engine()) as session:
                obj = (session.query(ArticlesURLs)
                            .filter(ArticlesURLs.id == self._article_id)
                            .one())
                obj.stage = ArticleStageEnum.ArticleGathered.value
                session.commit()#
        except Exception as ex:
            logger.error(f"ArticlesSecondaryInfoScraper._update_stage - Commit failed: {ex}")
            logger.info(f"\tdelete {self._article_id} from ArticleKeywords")
            with Session(get_engine()) as session:
                session.rollback()
                session.query(ArticleKeywords).filter(ArticleKeywords.article_id == self._article_id).delete()
                session.commit()
            logger.info(f"\tdelete {self._article_id} from Articles")
            with Session(get_engine()) as session:
                session.rollback()
                session.query(Articles).filter(Articles.id == self._article_id).delete()
                session.commit()
            raise ex 


    def entry_point(self):
        logger.info("ArticlesSecondaryInfoScraper.entry_point")
        self._get_article_url()
        self._get_articles_info()
        self._add_new_keywords()
        self._get_keywords_id()
        self._add_articles()
        self.add_keywords()
        self._update_stage()



if __name__ == "__main__":
    parser = ArticlesSecondaryInfoScraper(article_id=12)
    parser.entry_point()
