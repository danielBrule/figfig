from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Index, Float

Base = declarative_base()

class Newspaper(Base):
    __tablename__ = "newspaper"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

class ArticleStage(Base):
    __tablename__ = "article_stage"
    id = Column(Integer, primary_key=True)
    article_stage = Column(String(50), nullable=False)


class SitemapURLs(Base):
    __tablename__ = "sitemap_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(200), nullable=False)
    last_modification = Column(DateTime, nullable=False)
    to_process = Column(Boolean, nullable=False)    
    newspaper_id = Column(Integer, ForeignKey("newspaper.id"), nullable=False)
    insert_date = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('ix_sitemap_urls_url', 'url'),  # Create index on `url`
    )

    

class ArticlesURLs(Base):
    __tablename__ = "articles_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(400), nullable=False)
    last_modification = Column(DateTime, nullable=False)
    priority = Column(Float, nullable=False)
    source_id = Column(Integer, ForeignKey("sitemap_urls.id"), nullable=False)
    stage = Column(Integer, ForeignKey("article_stage.id"), nullable=False)    
    insert_date = Column(DateTime, nullable=False)
    __table_args__ = (
        Index('ix_articles_urls_url', 'url'),  # Create index on `url`
    )
    

class Keywords(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_keyword = Column(String(200), nullable=False)
    __table_args__ = (
        Index('keywords_full_keyword', 'full_keyword'),  
    )
    

    
class Articles(Base):
    __tablename__ = "articles"
    id = Column(Integer, ForeignKey("articles_urls.id"), primary_key=True)
    uid = Column(String(200), nullable=False)
    title = Column(String(500), nullable=False)
    publication_date = Column(DateTime, nullable=False)
    last_modification_date = Column(DateTime, nullable=False)
    description = Column(String(1000), nullable=False)
    insert_date = Column(DateTime, nullable=False)

class ArticleKeywords(Base):
    __tablename__ = "article_keywords"
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False, primary_key=True)


class Comments(Base):
    __tablename__ = "comments"
    id = Column(String(100), primary_key=True)
    comment = Column(String(2000), nullable=False)
    comment_date = Column(DateTime, nullable=False)
    replies_count = Column(Integer, nullable=False)
    sentiment = Column(Integer, nullable=True)
    contributor_id = Column(String(200), nullable=False)
    author_type = Column(String(200), nullable=False)
    parent_id = Column(String(100), ForeignKey("comments.id"), nullable=True, default=None)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    insert_date = Column(DateTime, nullable=False)
    __table_args__ = (
        Index('comments_contributor_id', 'contributor_id'),  
    )
    __table_args__ = (
        Index('comments_article_id', 'article_id'),  
    )

class Error(Base):
    __tablename__ = "errors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stage = Column(String(50), nullable=False)
    data_id = Column(String(400), nullable=False)
    error_type = Column(String(100), nullable=False)
    error_message = Column(String(1000), nullable=False)
    attempted_at = Column(DateTime, nullable=False)

