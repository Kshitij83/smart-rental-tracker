#!/usr/bin/env python3
"""
Test script to verify backend API connection and data
"""

import requests
import json

def test_backend_connection():
    """Test the backend API connection and data"""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Smart Rental Tracker Backend Connection")
    print("=" * 60)
    
    try:
        # Test 1: Basic connection
        print("1. Testing basic connection...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Backend is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend connection failed: {response.status_code}")
            return False
        
        # Test 2: Health check
        print("\n2. Testing health check...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test 3: Dashboard data
        print("\n3. Testing dashboard data...")
        response = requests.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard data retrieved")
            print(f"   Total Equipment: {data.get('overview', {}).get('total_equipment', 0)}")
            print(f"   Active Rentals: {data.get('overview', {}).get('active_rentals', 0)}")
            print(f"   Anomalies: {data.get('overview', {}).get('anomalies', 0)}")
            print(f"   Utilization Rate: {data.get('overview', {}).get('utilization_rate', 0)}%")
            
            # Check anomalies data
            anomalies = data.get('anomalies', {}).get('anomalies', [])
            print(f"   Anomalies Data Count: {len(anomalies)}")
            
            if anomalies:
                print("   Sample anomaly data:")
                for i, anomaly in enumerate(anomalies[:3]):
                    print(f"     {i+1}. {anomaly.get('equipment_id')} - {anomaly.get('site_id')} - {anomaly.get('type')}")
            
            # Check equipment stats
            equipment_stats = data.get('equipment_stats', {})
            if equipment_stats:
                print(f"   Equipment Stats: {equipment_stats.get('overview', {})}")
                
        else:
            print(f"❌ Dashboard data failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Test 4: Equipment list
        print("\n4. Testing equipment list...")
        response = requests.get(f"{base_url}/equipment/")
        if response.status_code == 200:
            equipment = response.json()
            print(f"✅ Equipment list retrieved: {len(equipment)} items")
            
            # Count equipment with site_id
            with_site = [eq for eq in equipment if eq.get('site_id')]
            without_site = [eq for eq in equipment if not eq.get('site_id')]
            
            print(f"   Equipment with site_id: {len(with_site)}")
            print(f"   Equipment without site_id: {len(without_site)}")
            
            if with_site:
                print("   Sample equipment with site:")
                for i, eq in enumerate(with_site[:3]):
                    print(f"     {i+1}. {eq.get('equipment_id')} - {eq.get('site_id')} - {eq.get('type')}")
                    
        else:
            print(f"❌ Equipment list failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎉 Backend connection test completed!")
        print("\n📋 Next steps:")
        print("1. Make sure the frontend is running on http://localhost:3000")
        print("2. Check the browser console for any errors")
        print("3. Look for the debug information in the dashboard")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running:")
        print("   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_backend_connection()
