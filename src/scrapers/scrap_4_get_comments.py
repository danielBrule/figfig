from sqlalchemy import select
from sqlalchemy.orm import Session

import json
import hashlib
from db.database import get_engine
from db.models import ArticlesURLs, Articles, Comments
from utils.log import logger
from utils.constants import ArticleStageEnum
from utils.helpers import simple_get
from utils.scraper import Scraper

URL_COMMENT = 'https://api-graphql.lefigaro.fr/graphql?id=widget-comments_commentsQuery2_31d9f1fd61a3568936b76800aef3aade1b9002eee01930e2b9c499ceca28192e&variables={{"id":"{}","page":{}}}'
URL_REPLY = 'https://api-graphql.lefigaro.fr/graphql?id=widget-comments_commentRepliesQuery2_f6f03af22e6093fb8d5a69caf102e33ae439b8587d763475a300e041d7985d10&variables={{"id":"{}"}}'

class CommentsScraper(Scraper):
    def __init__(self, article_id: int):
        logger.info("ArticlesInfo.__init__")
        self._article_id = article_id
        self._articles_uid = None
        self._comments = []

    def _get_article_uid(self):
        logger.info("Comments._get_article_url")
        stmt = select(Articles.uid).where(ArticlesURLs.id == self._article_id)
        with Session(get_engine()) as session:
            self._articles_uid = session.execute(stmt).scalar_one_or_none()
        logger.info(f"\tUID: {self._articles_uid}")
        
        
    def _get_author(self, node_author) -> str:
        if node_author is None:
            return ""
        name = node_author["username"] if  "username" in node_author else node_author["signature"]
        return hashlib.md5(name.encode("utf-8")).hexdigest()

    def _get_author_type(self, node_author) -> str:
        if node_author is None:
            return ""
        return node_author["__typename"]
    


    def _get_replies(self, comment_id: str) -> list:
        raw_json = simple_get(URL_REPLY.format(comment_id))
        comments = json.loads(raw_json)
        
        for comment in comments["data"]["commentReplies"]:
            self._comments.append(Comments(
                id= comment["id"],
                comment= comment["text"],
                comment_date= comment["createdAt"],
                replies_count= comment["repliesCount"],
                contributor_id= self._get_author(comment["author"]),
                author_type= self._get_author_type(comment["author"]),
                parent_id= comment_id,
                article_id= self._article_id,
                insert_date = self._now
            ))
            if comment["repliesCount"] > 0:
                self._get_replies(comment["id"])
        
        
    def _get_articles_comments(self):
        logger.info("Comments._get_articles_comments")

        page_cpt = 1

        while True:
            logger.info(f"Page {page_cpt}, # comments: {len(self._comments)}")
            raw_json = simple_get(URL_COMMENT.format(self._articles_uid, page_cpt))
            comments = json.loads(raw_json)
            if len(comments["data"]["comments"]) == 0:
                break
            for comment in comments["data"]["comments"]:
                self._comments.append(Comments(
                    id= comment["id"],
                    comment= comment["text"],
                    comment_date= comment["createdAt"],
                    replies_count= comment["repliesCount"],
                    contributor_id= self._get_author(comment["author"]),
                    author_type= self._get_author_type(comment["author"]),
                    parent_id= None,
                    article_id= self._article_id
                ))
                if comment["repliesCount"] > 0:
                     self._get_replies(comment["id"])
            page_cpt += 1
        

    def _add_new_comments(self):
        logger.info("Comments._add_new_comments")
        with Session(get_engine()) as session:
            session.add_all(self._comments)
            session.commit()

        logger.info(f"{len(self._comments)} new comments inserted into the database.")



    def _update_stage(self):
        logger.info("Comments._update_stage")
        try:
            with Session(get_engine()) as session:
                obj = (session.query(ArticlesURLs)
                            .filter(ArticlesURLs.id == self._article_id)
                            .one())
                obj.stage = ArticleStageEnum.CommentsGathered.value
                session.commit()#
        except Exception as ex:
            logger.error(f"ArticlesInfo._update_stage - Commit failed: {ex}")
            logger.info(f"\tdelete {self._article_id} from Comments")
            with Session(get_engine()) as session:
                session.rollback()
                session.query(Comments).filter(Comments.article_id == self._article_id).delete()
                session.commit()
            logger.info(f"\tdelete {self._article_id} from Comments")

            raise ex 


    def entry_point(self):
        logger.info("ArticlesInfo.entry_point")
        self._get_article_uid()
        self._get_articles_comments()
        self._add_new_comments()

        self._update_stage()



if __name__ == "__main__":
    parser = CommentsScraper(article_id=12)
    parser.entry_point()
