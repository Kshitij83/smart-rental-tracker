#!/usr/bin/env python3
"""
Enhanced ML Model Training Script for Smart Rental Tracker
Trains site-specific demand forecasting models with improved features
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

from smart_ml_system import SmartMLSystem

def main():
    print("🚀 Enhanced ML Model Training for Smart Rental Tracker")
    print("=" * 60)
    
    # Initialize the ML system
    print("\n📊 Initializing ML system...")
    ml_system = SmartMLSystem()
    
    if ml_system.data is None:
        print("❌ Failed to load data. Please check the data path.")
        return
    
    print(f"✅ Data loaded: {len(ml_system.data)} records")
    
    # Check if models are already trained
    if ml_system.models_trained:
        print("✅ Models are already trained!")
        
        # Test the demand forecasting
        print("\n🧪 Testing demand forecasting...")
        test_demand_forecasting(ml_system)
        
        # Test site-specific predictions
        print("\n🏗️ Testing site-specific predictions...")
        test_site_specific_predictions(ml_system)
        
        # Save models
        print("\n💾 Saving models...")
        ml_system.save_models()
        
    else:
        print("❌ Models failed to train. Check the data quality.")
    
    print("\n🎯 Training complete!")

def test_demand_forecasting(ml_system):
    """Test the demand forecasting functionality"""
    
    # Test global demand forecast
    print("  📈 Testing global demand forecast...")
    global_forecast = ml_system.forecast_demand(days_ahead=30)
    
    if 'error' not in global_forecast:
        print(f"    ✅ Global forecast generated: {global_forecast['forecast_days']} days")
        print(f"    📊 Total predicted demand: {global_forecast['total_predicted_demand']}")
        print(f"    📊 Average daily demand: {global_forecast['average_daily_demand']}")
        print(f"    📈 Trend: {global_forecast['trend']} (strength: {global_forecast['trend_strength']})")
    else:
        print(f"    ❌ Global forecast failed: {global_forecast['error']}")
    
    # Test equipment-specific forecast
    print("  🔧 Testing equipment-specific forecast...")
    equipment_forecast = ml_system.forecast_demand(
        equipment_type='Excavator', 
        days_ahead=30
    )
    
    if 'error' not in equipment_forecast:
        print(f"    ✅ Excavator forecast generated: {equipment_forecast['forecast_days']} days")
        print(f"    📊 Total predicted demand: {equipment_forecast['total_predicted_demand']}")
        print(f"    📈 Trend: {equipment_forecast['trend']}")
    else:
        print(f"    ❌ Equipment forecast failed: {equipment_forecast['error']}")

def test_site_specific_predictions(ml_system):
    """Test site-specific demand predictions"""
    
    # Get unique sites from data
    sites = ml_system.data['User ID'].unique()
    sites = [site for site in sites if site != 'UNASSIGNED'][:5]  # Test first 5 sites
    
    print(f"  🏗️ Testing {len(sites)} site-specific models...")
    
    for site in sites:
        print(f"    📍 Testing site {site}...")
        
        # Test site-specific forecast
        site_forecast = ml_system.forecast_demand(
            site_id=site, 
            days_ahead=30
        )
        
        if 'error' not in site_forecast:
            print(f"      ✅ Site {site} forecast: {site_forecast['total_predicted_demand']:.1f} total demand")
            print(f"      📈 Trend: {site_forecast['trend']} (strength: {site_forecast['trend_strength']})")
            
            # Test equipment-specific forecast for this site
            equipment_site_forecast = ml_system.forecast_demand(
                equipment_type='Bulldozer',
                site_id=site,
                days_ahead=30
            )
            
            if 'error' not in equipment_site_forecast:
                print(f"      🔧 Bulldozer at {site}: {equipment_site_forecast['total_predicted_demand']:.1f} total demand")
            else:
                print(f"      ❌ Equipment-site forecast failed: {equipment_site_forecast['error']}")
        else:
            print(f"      ❌ Site {site} forecast failed: {site_forecast['error']}")

def analyze_data_quality(ml_system):
    """Analyze the quality of the training data"""
    print("\n📊 Data Quality Analysis")
    print("-" * 30)
    
    data = ml_system.data
    
    # Basic statistics
    print(f"Total records: {len(data)}")
    print(f"Equipment types: {data['Type'].nunique()}")
    print(f"Sites: {data['User ID'].nunique()}")
    print(f"Date range: {data['Check-Out Date'].min()} to {data['Check-Out Date'].max()}")
    
    # Check for missing values
    missing_data = data.isnull().sum()
    print(f"\nMissing values:")
    for col, count in missing_data.items():
        if count > 0:
            print(f"  {col}: {count} ({count/len(data)*100:.1f}%)")
    
    # Equipment type distribution
    print(f"\nEquipment type distribution:")
    equipment_counts = data['Type'].value_counts()
    for eq_type, count in equipment_counts.items():
        print(f"  {eq_type}: {count} ({count/len(data)*100:.1f}%)")
    
    # Site distribution
    print(f"\nSite distribution (top 10):")
    site_counts = data['User ID'].value_counts().head(10)
    for site, count in site_counts.items():
        print(f"  {site}: {count} ({count/len(data)*100:.1f}%)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
