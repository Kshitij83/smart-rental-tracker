#!/usr/bin/env python3
"""
Production startup script for Smart Rental Tracker Backend
This script handles database initialization and starts the FastAPI server
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from app.database import engine
from app import models
from app.populate_database import clear_and_populate_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database tables and populate with sample data"""
    try:
        logger.info("Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        logger.info("Populating database with sample data...")
        clear_and_populate_database()
        logger.info("Database populated successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def main():
    """Main startup function"""
    logger.info("🚀 Starting Smart Rental Tracker Backend...")
    
    # Initialize database
    initialize_database()
    
    # Start the FastAPI server
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()