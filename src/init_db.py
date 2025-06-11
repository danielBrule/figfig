from dotenv import load_dotenv
load_dotenv()



from sqlalchemy.orm import Session

from db.database import engine
from db.models import Base, Newspaper, ArticleStage
from utils.constants import NewspaperEnum, ArticleStageEnum
from utils.log import logger

def create_tables():
    logger.info("create_tables")
    logger.info("\tDrop tables ")
    Base.metadata.drop_all(bind=engine)
    logger.info("\tCreate tables")
    Base.metadata.create_all(bind=engine)
    logger.info("\t✅ Tables created.")


def init_tables():
    logger.info("init_tables")
    l_data_newspaper = []
    for member in NewspaperEnum:
        l_data_newspaper.append(Newspaper(id= member.value, name=member.name))
    with Session(engine) as session:
        session.add_all(l_data_newspaper)
        session.commit()
    
    l_data_stage = []
    for member in ArticleStageEnum:
        l_data_stage.append(ArticleStage(id= member.value, article_stage=member.name))
    with Session(engine) as session:
        session.add_all(l_data_stage)
        session.commit()
    logger.info("\t✅ Tables Initialised.")
            

# Create all tables defined in Base metadata
if __name__ == "__main__":
    
    logger.info("initialise data base")
    create_tables()
    init_tables()