from dotenv import load_dotenv

load_dotenv()
from utils.db import create_tables, init_tables
from utils.log import logger


# Create all tables defined in Base metadata
if __name__ == "__main__":

    logger.info("initialise data base")
    create_tables()
    init_tables()
