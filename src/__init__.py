import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

def get_engine():
    """
    Creates and returns a SQLAlchemy engine configured from .env variables.
    """
    load_dotenv()
    
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_host, db_port, db_name]):
        raise ValueError("Database credentials are not fully set in the .env file.")

    connection_string = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    return create_engine(connection_string)
