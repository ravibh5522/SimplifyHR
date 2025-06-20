# ai_hr_jd_project/database/connection.py
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
from .models import Base # Import Base from models.py
from config import Config

# Global engine and SessionLocal
engine = None
SessionLocal = None

def init_connection_pool() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.
    Uses the Cloud SQL Python Connector package.
    """
    instance_connection_name = Config.INSTANCE_CONNECTION_NAME
    db_user = Config.DB_USER
    db_pass = Config.DB_PASS
    db_name = Config.DB_NAME

    if not all([instance_connection_name, db_user, db_pass, db_name]):
        raise ValueError(
            "Missing Cloud SQL connection parameters. "
            "Ensure DB_USER, DB_PASS, DB_NAME, and INSTANCE_CONNECTION_NAME are set."
        )

    ip_type = IPTypes.PRIVATE if Config.PRIVATE_IP else IPTypes.PUBLIC

    connector = Connector(ip_type=ip_type)
    def getconn() -> pymysql.connections.Connection:
        if instance_connection_name is None:
            raise ValueError("INSTANCE_CONNECTION_NAME must not be None")
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
            connect_timeout=30 # Add a timeout
        )
        return conn
        return conn

    # The 'creator' argument is used to specify a custom connection function
    pool = create_engine(
        Config.get_db_uri(), # e.g., "mysql+pymysql://"
        creator=getconn,
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800, # e.g., recycle connections every 30 minutes
    )
    return pool

def init_db():
    global engine, SessionLocal
    if engine is None:
        engine = init_connection_pool()
        SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created (if they didn't exist).")

def get_db():
    if SessionLocal is None:
        raise Exception("Database not initialized. Call init_db() first.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Call init_db() when this module is imported or at app startup
# For robust applications, this might be better placed in app.py's app creation factory.
# init_db() # We will call this in app.py