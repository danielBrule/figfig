from enum import Enum

NAMESPACE = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

class NewspaperEnum(Enum):
    Lefigaro = 1
    LeMonde = 2
    Liberation = 3
class ArticleStageEnum(Enum):
    UrlGathered = 1
    ArticleGathered = 2 
    CommentsGathered = 3 