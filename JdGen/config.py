# ai_hr_jd_project/config.py
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

class Config:
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_NAME = os.environ.get("DB_NAME")
    INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
    PRIVATE_IP = os.environ.get("PRIVATE_IP", "false").lower() == "true"

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Suppress warning

    @staticmethod
    def get_db_uri():
        # This URI is a placeholder for SQLAlchemy with the connector,
        # the actual connection is handled by the connector's getconn.
        return f"mysql+pymysql://"