from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def build_database_url():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_name = os.getenv("POSTGRES_DB", "kaouka_db")
    db_user = os.getenv("POSTGRES_USER", "kaoukakeet")
    db_password = os.getenv("POSTGRES_PASSWORD", "indestructible")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


engine = create_engine(build_database_url(), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def init_db():
    # Local import to avoid circular imports when metadata is loaded.
    from schema import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

