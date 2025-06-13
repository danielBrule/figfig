from dotenv import load_dotenv
import os

def pytest_configure():
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env.dev")
    load_dotenv(dotenv_path)