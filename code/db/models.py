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
    
class Contributors(Base):
    __tablename__ = "contributors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    Contributor_name = Column(String(150), nullable=False)
    newspaper = Column(Integer, nullable=False)
    __table_args__ = (
        Index('contributors_Contributor_name', 'Contributor_name'),  
    )
    
class Articles(Base):
    __tablename__ = "articles"
    id = Column(Integer, ForeignKey("articles_urls.id"), primary_key=True)
    uid = Column(String(200), nullable=False)
    title = Column(String(500), nullable=False)
    publication_date = Column(DateTime, nullable=False)
    last_modification_date = Column(DateTime, nullable=False)
    description = Column(String(1000), nullable=False)
    

class ArticleKeywords(Base):
    __tablename__ = "article_keywords"
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False, primary_key=True)


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    comment = Column(String(2000), nullable=False)
    comment_Date = Column(DateTime, nullable=False)
    is_journaliste = Column(Boolean, nullable=False)
    has_child = Column(Boolean, nullable=False)
    sentiment = Column(Integer, nullable=True)
    contributors_id = Column(Integer, ForeignKey("contributors.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True, default=None)



