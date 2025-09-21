#!/usr/bin/env python3
"""
Script to populate the database with data from CSV file
"""

import pandas as pd
import os
from sqlalchemy.orm import sessionmaker
from .models import Base, Equipment
from .database import engine, SessionLocal

def clear_and_populate_database():
    """Clear existing data and populate with CSV data"""
    
    # Create all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Read CSV data
    csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'data.csv')
    print(f"Reading CSV from: {csv_path}")
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    print(f"Found {len(df)} records in CSV")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Process each row in the CSV
        for index, row in df.iterrows():
            # Handle NULL values from CSV
            site_id = row['User ID'] if pd.notna(row['User ID']) else None
            last_operator_id = row['Last Operator ID'] if pd.notna(row['Last Operator ID']) else None
            check_out_date = row['Check-Out Date'] if pd.notna(row['Check-Out Date']) else None
            check_in_date = row['Check-in Date'] if pd.notna(row['Check-in Date']) else None
            
            # Create equipment record
            equipment = Equipment(
                equipment_id=row['Equipment ID'],
                type=row['Type'],
                site_id=site_id,
                check_out_date=check_out_date,
                check_in_date=check_in_date,
                engine_hours_per_day=float(row['Engine Hours/Day']) if pd.notna(row['Engine Hours/Day']) else 0.0,
                idle_hours_per_day=float(row['Idle Hours/Day']) if pd.notna(row['Idle Hours/Day']) else 0.0,
                operating_days=int(row['Operating Days']) if pd.notna(row['Operating Days']) else 0,
                last_operator_id=last_operator_id,
                status="rented" if site_id else "available",
                manufacturer="Caterpillar",  # Default manufacturer
                year=2020 + (index % 5),  # Assign years 2020-2024 cyclically
            )
            
            db.add(equipment)
            
            if index % 50 == 0:
                print(f"Processed {index + 1} records...")
        
        # Commit all changes
        db.commit()
        print(f"Successfully populated database with {len(df)} equipment records!")
        
        # Verify the data
        count = db.query(Equipment).count()
        print(f"Total equipment records in database: {count}")
        
        # Show some sample data
        sample_equipment = db.query(Equipment).limit(5).all()
        print("\nSample equipment records:")
        for eq in sample_equipment:
            print(f"- {eq.equipment_id}: {eq.type} (Site: {eq.site_id}, Status: {eq.status})")
            
    except Exception as e:
        db.rollback()
        print(f"Error populating database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting database population...")
    clear_and_populate_database()
    print("✅ Database population completed!")
