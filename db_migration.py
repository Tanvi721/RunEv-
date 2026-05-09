import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.database import engine
from sqlalchemy import text

def run_migration():
    commands = [
        "ALTER TABLE providers ADD COLUMN charging_speed VARCHAR(255);",
        "ALTER TABLE providers ADD COLUMN connector_types VARCHAR(255);",
        "ALTER TABLE providers ADD COLUMN price_per_kwh FLOAT;"
    ]
    with engine.begin() as conn:
        for cmd in commands:
            try:
                conn.execute(text(cmd))
                print(f"Executed: {cmd}")
            except Exception as e:
                if 'Duplicate column name' in str(e):
                    print(f"Column already exists: {cmd}")
                else:
                    print(f"Error executing {cmd}: {e}")

if __name__ == '__main__':
    run_migration()
