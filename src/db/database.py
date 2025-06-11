from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import os 
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from utils.log import logger



KEY_VAULT_NAME = os.getenv("KEY_VAULT_NAME")
KV_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KV_URI, credential=credential)



logger.info(f"KEY_VAULT_NAME: {KEY_VAULT_NAME}")

SERVER = os.getenv("DB_SERVER")
DATABASE = os.getenv("DB_NAME")
USERNAME = os.getenv("DB_USER")
PASSWORD = client.get_secret("db-password").value

# Or whatever version you installed
DRIVER = os.getenv("DB_DRIVER")


# SQLAlchemy connection string
connection_string = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}:1433/{DATABASE}?driver={DRIVER.replace(' ', '+')}"

logger.info(f"connection_string: {connection_string}")

# Create engine
engine = create_engine(connection_string)
session = Session(engine)