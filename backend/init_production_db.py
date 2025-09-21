#!/usr/bin/env python3
"""
Production Database Initialization Script
This script ensures the database is properly initialized when deployed on Render
"""

import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.database import engine
from app import models
from app.crud import init_db

def init_production_database():
    """Initialize the production database"""
    try:
        print("🚀 Initializing production database...")
        
        # Create all tables
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Initialize with sample data if database is empty
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            # Check if database has data
            equipment_count = db.query(models.Equipment).count()
            
            if equipment_count == 0:
                print("📊 Database is empty, initializing with sample data...")
                init_db(db)
                print("✅ Sample data initialized successfully")
            else:
                print(f"📊 Database already contains {equipment_count} equipment records")
                
        finally:
            db.close()
            
        print("🎉 Production database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing production database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_production_database()
