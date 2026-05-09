from sqlalchemy import inspect, text

from backend.database import engine


inspector = inspect(engine)
if "providers" not in inspector.get_table_names():
    print("providers table not found. Run init_db or migrations first.")
    raise SystemExit(1)

columns = [column["name"] for column in inspector.get_columns("providers")]
request_columns = [column["name"] for column in inspector.get_columns("service_requests")] if "service_requests" in inspector.get_table_names() else []
payment_columns = [column["name"] for column in inspector.get_columns("payments")] if "payments" in inspector.get_table_names() else []
commands = []

for column_name, column_type in (
    ("profile_photo", "VARCHAR(512)"),
    ("driver_name", "VARCHAR(255)"),
    ("address", "VARCHAR(512)"),
):
    if column_name not in columns:
        commands.append(f"ALTER TABLE providers ADD COLUMN {column_name} {column_type}")

if "charged_units_kwh" not in request_columns:
    commands.append("ALTER TABLE service_requests ADD COLUMN charged_units_kwh FLOAT")

if "total_price" not in request_columns:
    commands.append("ALTER TABLE service_requests ADD COLUMN total_price FLOAT")

if "payment_method" not in request_columns:
    commands.append("ALTER TABLE service_requests ADD COLUMN payment_method VARCHAR(255) DEFAULT 'CASH'")

for column_name, column_type in (
    ("request_id", "INT"),
    ("booking_id", "INT"),
    ("user_id", "INT"),
    ("razorpay_order_id", "VARCHAR(255)"),
    ("razorpay_payment_id", "VARCHAR(255)"),
    ("amount", "FLOAT"),
    ("status", "VARCHAR(255)"),
):
    if "payments" in inspector.get_table_names() and column_name not in payment_columns:
        commands.append(f"ALTER TABLE payments ADD COLUMN {column_name} {column_type}")

for index in inspector.get_indexes("providers"):
    if index.get("unique") and index.get("column_names") == ["user_id"]:
        index_name = index["name"]
        if engine.dialect.name == "sqlite":
            commands.append(f"DROP INDEX {index_name}")
        else:
            commands.append(f"ALTER TABLE providers DROP INDEX {index_name}")

if not commands:
    print("All provider columns and indexes already support fleet vans.")
else:
    with engine.begin() as conn:
        for command in commands:
            try:
                conn.execute(text(command))
                print(f"Executed: {command}")
            except Exception as exc:
                error_text = str(exc).lower()
                if "duplicate column name" in error_text or "already exists" in error_text:
                    print(f"Already exists: {command}")
                else:
                    print(f"Error executing {command}: {exc}")
    print("Database schema updated successfully.")
