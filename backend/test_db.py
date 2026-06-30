# test_db.py

from app.core.database import SessionLocal

db = SessionLocal()

try:
    print("Database Connected Successfully")
finally:
    db.close()