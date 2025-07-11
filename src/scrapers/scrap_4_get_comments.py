from sqlalchemy import select
from sqlalchemy.orm import Session
import os 
import json
import hashlib
from db.database import get_engine
from db.models import ArticlesURLs, Articles, Comments
from utils.log import logger
from utils.constants import ArticleStageEnum
from utils.helpers import simple_get
from utils.scraper import Scraper
from utils.constants import ServiceQueue

URL_COMMENT = 'https://api-graphql.lefigaro.fr/graphql?id=widget-comments_commentsQuery2_31d9f1fd61a3568936b76800aef3aade1b9002eee01930e2b9c499ceca28192e&variables={{"id":"{}","page":{}}}'
URL_REPLY = 'https://api-graphql.lefigaro.fr/graphql?id=widget-comments_commentRepliesQuery2_f6f03af22e6093fb8d5a69caf102e33ae439b8587d763475a300e041d7985d10&variables={{"id":"{}"}}'


class CommentsScraper(Scraper):
    def __init__(self):
        logger.info("CommentsScraper.__init__")
        super().__init__()
        self._stage = "CommentsScraper"
        self._article_id = None
        self._articles_uid = None
        self._comments = []
        self._service_bus_queue_source = ServiceQueue.comments.value

    def _get_article_uid(self):
        logger.info("Comments._get_article_url")
        stmt = select(Articles.uid).where(ArticlesURLs.id == self._article_id)
        with Session(get_engine()) as session:
            self._articles_uid = session.execute(stmt).scalar_one_or_none()
        logger.info(f"\tUID: {self._articles_uid}")

    def _get_author(self, node_author) -> str:
        if node_author is None:
            return ""
        name = (
            node_author["username"]
            if "username" in node_author
            else node_author["signature"]
        )
        if name is None:
            return ""
        return hashlib.md5(name.encode("utf-8")).hexdigest()

    def _get_author_type(self, node_author) -> str:
        if node_author is None:
            return ""
        return node_author["__typename"]

    def _get_replies(self, comment_id: str) -> list:
        raw_json = simple_get(URL_REPLY.format(comment_id))
        comments = json.loads(raw_json)

        for comment in comments["data"]["commentReplies"]:
            self._comments.append(
                Comments(
                    id=comment["id"],
                    comment=comment["text"],
                    comment_date=comment["createdAt"],
                    replies_count=comment["repliesCount"],
                    contributor_id=self._get_author(comment["author"]),
                    author_type=self._get_author_type(comment["author"]),
                    parent_id=comment_id,
                    article_id=self._article_id,
                    insert_date=self._now,
                )
            )
            if comment["repliesCount"] > 0:
                self._get_replies(comment["id"])

    def _get_articles_comments(self):
        logger.info("Comments._get_articles_comments")

        page_cpt = 1

        while True:
            try:
                logger.info(f"\tPage {page_cpt}, # comments: {len(self._comments)}")
                raw_json = simple_get(URL_COMMENT.format(self._articles_uid, page_cpt))
                comments = json.loads(raw_json)
                if len(comments["data"]["comments"]) == 0:
                    break
                for comment in comments["data"]["comments"]:
                    try: 
                        self._comments.append(
                            Comments(
                                id=comment["id"],
                                comment=comment["text"],
                                comment_date=comment["createdAt"],
                                replies_count=comment["repliesCount"],
                                contributor_id=self._get_author(comment["author"]),
                                author_type=self._get_author_type(comment["author"]),
                                parent_id=None,
                                article_id=self._article_id,
                                insert_date=self._now,
                            )
                        )
                        if comment["repliesCount"] > 0:
                            try:
                                self._get_replies(comment["id"])
                            except Exception as e:
                                logger.error(f"\tError while fetching replies for comment {comment['id']}: {e}")
                                continue
                    except Exception as e:
                        logger.error(f"\tError while processing comment {comment['id']}: {e}")
                        continue
            except Exception as e:
                logger.error(f"\tError while fetching comments: {e}")
                self._error_recovery()
                continue
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
                obj = (
                    session.query(ArticlesURLs)
                    .filter(ArticlesURLs.id == self._article_id)
                    .one()
                )
                obj.stage = ArticleStageEnum.CommentsGathered.value
                session.commit()  #
        except Exception as ex:
            logger.error(f"ArticlesInfo._update_stage - Commit failed: {ex}")
            logger.info(f"\tdelete {self._article_id} from Comments")
            with Session(get_engine()) as session:
                session.rollback()
                session.query(Comments).filter(
                    Comments.article_id == self._article_id
                ).delete()
                session.commit()
            logger.info(f"\tdelete {self._article_id} from Comments")

            raise ex

    def _error_recovery(self) -> None:
        # todo
        pass

    @staticmethod
    def entry_point(article_id: int = None):
        logger.info("ArticlesInfo.entry_point")

        scraper = CommentsScraper()
        if article_id is None:
            scraper.get_one_message()
            scraper._article_id = int(str(scraper._servicebus_source_message))
            if scraper._servicebus_source_message is None:
                logger.info("No messages to process in the queue.")
                return

        else:
            scraper._article_id = article_id

        if scraper._article_id is not None:
            logger.info(f"Processing: {scraper._article_id}")
            try:
                scraper._get_article_uid()
                scraper._get_articles_comments()
                scraper._add_new_comments()

                scraper._update_stage()
                scraper.complete_message()
            except Exception as e:
                logger.error(f"Error: {e}")
                scraper.abandon_message()
                scraper.log_scraper_error(id=scraper._article_id, error=e)
    logger.info("CommentsScraper completed successfully.")


if __name__ == "__main__":
    if os.getenv("ON_AZURE") is not None and os.getenv("ON_AZURE").lower() == "true":
        CommentsScraper.entry_point()
    else:   
        CommentsScraper.entry_point(article_id=12)
