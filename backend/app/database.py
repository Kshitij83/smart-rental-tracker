from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - supports both local development and production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/rental.db")

# For production (Render), use the provided DATABASE_URL
# For local development, use SQLite
if DATABASE_URL.startswith("postgres://"):
    # PostgreSQL for production
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # SQLite for development
    current_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(current_dir, "rental.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{database_path}"

# Create engine
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    # PostgreSQL for production
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # SQLite for development
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}  # needed for SQLite
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
