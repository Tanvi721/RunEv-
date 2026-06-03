import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import text
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


def ensure_auth_security_columns() -> None:
    statements = [
        "ALTER TABLE users ADD COLUMN auth_provider VARCHAR(32) DEFAULT 'email'",
        "ALTER TABLE users ADD COLUMN created_at DATETIME",
        "ALTER TABLE users ADD COLUMN last_login_at DATETIME",
        "ALTER TABLE users ADD COLUMN failed_login_count INTEGER DEFAULT 0 NOT NULL",
        "ALTER TABLE users ADD COLUMN locked_until DATETIME",
        "UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL",
        "UPDATE users SET failed_login_count = 0 WHERE failed_login_count IS NULL",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_providers_vehicle_number_idx ON providers(vehicle_number)",
        "CREATE INDEX IF NOT EXISTS ix_users_failed_login ON users(email, failed_login_count, locked_until)",
    ]
    with engine.begin() as conn:
        for statement in statements:
            try:
                conn.execute(text(statement))
            except Exception as exc:
                message = str(exc).lower()
                if "duplicate column" in message or "already exists" in message:
                    continue
                print(f"RunEV schema upgrade skipped statement: {statement} ({exc})")


def ensure_pricing_columns() -> None:
    statements = [
        """
        CREATE TABLE IF NOT EXISTS pricing_settings (
            id INTEGER PRIMARY KEY,
            base_visit_fee FLOAT NOT NULL DEFAULT 99,
            distance_rate_per_km FLOAT NOT NULL DEFAULT 12,
            charging_rate_per_kwh FLOAT NOT NULL DEFAULT 20,
            platform_fee FLOAT NOT NULL DEFAULT 20,
            emergency_fee_limit FLOAT NOT NULL DEFAULT 0,
            night_fee_limit FLOAT NOT NULL DEFAULT 0,
            updated_at DATETIME
        )
        """,
        "INSERT INTO pricing_settings (id, base_visit_fee, distance_rate_per_km, charging_rate_per_kwh, platform_fee, emergency_fee_limit, night_fee_limit, updated_at) SELECT 1, 99, 12, 20, 20, 0, 0, CURRENT_TIMESTAMP WHERE NOT EXISTS (SELECT 1 FROM pricing_settings WHERE id = 1)",
        "ALTER TABLE service_requests ADD COLUMN estimated_distance_km FLOAT",
        "ALTER TABLE service_requests ADD COLUMN base_visit_fee FLOAT",
        "ALTER TABLE service_requests ADD COLUMN distance_rate_per_km FLOAT",
        "ALTER TABLE service_requests ADD COLUMN charging_rate_per_kwh FLOAT",
        "ALTER TABLE service_requests ADD COLUMN platform_fee FLOAT",
        "ALTER TABLE service_requests ADD COLUMN distance_charge FLOAT",
        "ALTER TABLE service_requests ADD COLUMN charging_cost FLOAT",
        "ALTER TABLE service_requests ADD COLUMN emergency_fee FLOAT DEFAULT 0 NOT NULL",
        "ALTER TABLE service_requests ADD COLUMN night_fee FLOAT DEFAULT 0 NOT NULL",
        "ALTER TABLE service_requests ADD COLUMN driver_earnings FLOAT",
        "ALTER TABLE service_requests ADD COLUMN runev_earnings FLOAT",
        "ALTER TABLE service_requests ADD COLUMN charging_revenue FLOAT",
    ]
    with engine.begin() as conn:
        for statement in statements:
            try:
                conn.execute(text(statement))
            except Exception as exc:
                message = str(exc).lower()
                if "duplicate column" in message or "already exists" in message:
                    continue
                print(f"RunEV pricing schema upgrade skipped statement: {statement} ({exc})")
