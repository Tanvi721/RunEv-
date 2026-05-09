import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD")
    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_db = os.getenv("MYSQL_DB")
    if mysql_user and mysql_password and mysql_db:
        from urllib.parse import quote_plus
        password = quote_plus(mysql_password)
        DATABASE_URL = f"mysql+pymysql://{mysql_user}:{password}@{mysql_host}:{mysql_port}/{mysql_db}"

# Use SQLite by default if no other database settings are available
SQLALCHEMY_DATABASE_URL = DATABASE_URL or "sqlite:///./runev.db"

def make_engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)

try:
    engine = make_engine(SQLALCHEMY_DATABASE_URL)
    if not SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            pass
except Exception as exc:
    print("WARNING: could not connect to the configured database. Falling back to local SQLite.")
    print(f"  Error: {exc}")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./runev.db"
    engine = make_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
