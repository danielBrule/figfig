from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import os 
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from utils.log import logger

_engine = None
# Create engine
def get_engine():
    global _engine
    if _engine is None:
        
        # get KV
        KEY_VAULT_NAME = os.getenv("KEY_VAULT_NAME")
        KV_URI = f"https://{KEY_VAULT_NAME}.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KV_URI, credential=credential)

        # Get database credentials from Azure Key Vault / enb
        SERVER = os.getenv("DB_SERVER")
        DATABASE = os.getenv("DB_NAME")
        USERNAME = os.getenv("DB_USER")
        PASSWORD = client.get_secret("db-password").value
        DRIVER = os.getenv("DB_DRIVER")

        # SQLAlchemy connection string
        connection_string = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}:1433/{DATABASE}?driver={DRIVER.replace(' ', '+')}"
        logger.info(f"KEY_VAULT_NAME: {KEY_VAULT_NAME}")


        logger.info(f"connection_string: {connection_string}")
        _engine = create_engine(connection_string)
    return _engine

# engine = get_engine()
# def get_session():
#     global _session
#     if 'session' not in globals():
#         logger.info("Creating a new database session")
#         _session = Session(engine)
#     return _session