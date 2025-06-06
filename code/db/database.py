from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os 

load_dotenv()


SERVER = os.getenv("DB_SERVER")
DATABASE = os.getenv("DB_NAME")
USERNAME = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")

# Or whatever version you installed
DRIVER = os.getenv("DB_DRIVER")


# SQLAlchemy connection string
connection_string = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}:1433/{DATABASE}?driver={DRIVER.replace(' ', '+')}"

print(f"{connection_string}")




# Create engine
engine = create_engine(connection_string)
session = Session(engine)