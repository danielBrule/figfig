from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Index

Base = declarative_base()

class SitemapURLs(Base):
    __tablename__ = "sitemap_urls"
    url = Column(String(200), nullable=False)
    last_modification = Column(DateTime, nullable=False)
    to_process = Column(Boolean, nullable=False)    
    
    __table_args__ = (
        Index('ix_sitemap_urls_url', 'url'),  # Create index on `url`
    )

class Keywords(Base):
    __tablename__ = "keywords"
    id = Column(String(200), primary_key=True)
    full_keyword = Column(String(200), nullable=False)

class Contributors(Base):
    __tablename__ = "contributors"
    id = Column(String(150), primary_key=True)

class Articles(Base):
    __tablename__ = "articles"
    id = Column(String(19), primary_key=True)
    title = Column(String(500), nullable=False)
    publication_date = Column(DateTime, nullable=False)
    last_modification_date = Column(DateTime, nullable=False)
    newspaper = Column(String(10), nullable=False)
    url = Column(String(200), nullable=False)
    has_been_parsed = Column(Integer, nullable=False)
    

class ArticleKeywords(Base):
    __tablename__ = "article_keywords"
    article_id = Column(String(19), ForeignKey("articles.id"), nullable=False, primary_key=True)
    keyword_id = Column(String(200), ForeignKey("keywords.id"), nullable=False, primary_key=True)


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    comment = Column(String(2000), nullable=False)
    comment_Date = Column(DateTime, nullable=False)
    is_journaliste = Column(Boolean, nullable=False)
    has_child = Column(Boolean, nullable=False)
    sentiment = Column(Integer, nullable=True)
    contributors_id = Column(String(150), ForeignKey("contributors.id"), nullable=False)
    article_id = Column(String(19), ForeignKey("articles.id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True, default=None)



