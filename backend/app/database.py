from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import shutil

current_dir = os.path.dirname(os.path.abspath(__file__))
bundle_db = os.path.join(current_dir, "rental.db")

db_path = os.environ.get("RENTAL_DB_PATH", bundle_db)

if db_path != bundle_db and os.path.exists(bundle_db) and not os.path.exists(db_path):
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        shutil.copy(bundle_db, db_path)
        print(f"Copied bundled database to {db_path}")
    except Exception as e:
        print(f"Could not copy database to {db_path}: {e}")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
