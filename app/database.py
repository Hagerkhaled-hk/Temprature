# الاتصال بالـ DB
import os
import certifi
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool

load_dotenv()

# Where the database lives. Default: a local SQLite file.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./temperature.db")

# SQLite needs this extra option; other databases don't.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}


if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # serverless: no long-lived connections
        connect_args={"ssl": {"ca": certifi.where()}},
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)



class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()