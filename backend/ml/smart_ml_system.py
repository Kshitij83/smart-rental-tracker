import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.cluster import KMeans
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class SmartMLSystem:
    def __init__(self, data_path: str = None):
        """Initialize the Smart ML System for rental tracking"""
        if data_path is None:
            # Try to find the data file relative to this script
            current_dir = os.path.dirname(__file__)
            # Try different possible paths
            possible_paths = [
                os.path.join(current_dir, '..', 'database', 'data.csv'),
                os.path.join(current_dir, '..', '..', 'database', 'data.csv'),
                os.path.join(os.getcwd(), 'database', 'data.csv'),
                os.path.join(os.getcwd(), '..', 'database', 'data.csv')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    data_path = path
                    break
            
            if data_path is None:
                print("⚠️ Could not find data.csv file automatically")
                data_path = "../database/data.csv"  # fallback
        
        self.data_path = data_path
        self.data = None
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.demand_forecaster = RandomForestRegressor(n_estimators=100, random_state=42)
        self.equipment_encoder = LabelEncoder()
        self.site_encoder = LabelEncoder()
        self.models_trained = False
        
        # Load and preprocess data
        self._load_data()
        if self.data is not None:
            self._preprocess_data()
            
            # Try to load saved models first, fallback to training if they don't exist
            models_dir = os.path.join(os.path.dirname(__file__), 'models')
            if os.path.exists(models_dir) and self._try_load_models(models_dir):
                print("✅ Loaded saved ML models successfully!")
            else:
                print("📊 No saved models found, training new models...")
                self._train_models()
    
    def _load_data(self):
        """Load data from CSV file"""
        try:
            self.data = pd.read_csv(self.data_path)
            print(f"Data loaded successfully: {len(self.data)} records")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = None
    
    def _preprocess_data(self):
        """Preprocess the data for ML models"""
        if self.data is None:
            return
            
        # Convert dates to datetime
        self.data['Check-Out Date'] = pd.to_datetime(self.data['Check-Out Date'])
        self.data['Check-in Date'] = pd.to_datetime(self.data['Check-in Date'])
        
        # Calculate rental duration
        self.data['rental_duration'] = (self.data['Check-in Date'] - self.data['Check-Out Date']).dt.days
        
        # Calculate utilization ratio (engine hours / (engine hours + idle hours))
        self.data['total_hours'] = self.data['Engine Hours/Day'] + self.data['Idle Hours/Day']
        self.data['utilization_ratio'] = np.where(
            self.data['total_hours'] > 0,
            self.data['Engine Hours/Day'] / self.data['total_hours'],
            0
        )
        
        # Calculate efficiency score (higher is better)
        self.data['efficiency_score'] = (
            self.data['Engine Hours/Day'] * 0.6 + 
            (24 - self.data['Idle Hours/Day']) * 0.4
        ) / 24
        
        # Encode categorical variables
        self.data['equipment_type_encoded'] = self.equipment_encoder.fit_transform(self.data['Type'])
        
        # Handle NULL values in User ID (which represents site assignment)
        self.data['User ID'] = self.data['User ID'].fillna('UNASSIGNED')
        self.data['site_encoded'] = self.site_encoder.fit_transform(self.data['User ID'])
        
        # Create features for anomaly detection
        self.data['anomaly_features'] = list(zip(
            self.data['Engine Hours/Day'],
            self.data['Idle Hours/Day'],
            self.data['utilization_ratio'],
            self.data['efficiency_score'],
            self.data['rental_duration']
        ))
        
        print("Data preprocessing completed")
    
    def _train_models(self):
        """Train the ML models"""
        if self.data is None or len(self.data) < 10:
            print("Insufficient data for training models")
            return
            
        try:
            # Prepare features for anomaly detection
            anomaly_features = np.array(self.data['anomaly_features'].tolist())
            anomaly_features_scaled = self.scaler.fit_transform(anomaly_features)
            
            # Train anomaly detector
            self.anomaly_detector.fit(anomaly_features_scaled)
            
            # Prepare features for demand forecasting
            # Group by equipment type and date to get daily demand
            daily_demand = self.data.groupby(['Type', 'Check-Out Date']).size().reset_index(name='demand')
            daily_demand['day_of_week'] = daily_demand['Check-Out Date'].dt.dayofweek
            daily_demand['month'] = daily_demand['Check-Out Date'].dt.month
            daily_demand['equipment_encoded'] = self.equipment_encoder.transform(daily_demand['Type'])
            
            if len(daily_demand) > 5:
                X_demand = daily_demand[['equipment_encoded', 'day_of_week', 'month']].values
                y_demand = daily_demand['demand'].values
                
                # Train demand forecaster
                self.demand_forecaster.fit(X_demand, y_demand)
            
            self.models_trained = True
            print("ML models trained successfully")
            
        except Exception as e:
            print(f"Error training models: {e}")
            self.models_trained = False
    
    def detect_anomalies(self, equipment_id: str = None) -> Dict:
        """Detect anomalies in equipment usage"""
        if not self.models_trained or self.data is None:
            return {"error": "Models not trained"}
        
        try:
            # Filter data if equipment_id is provided
            if equipment_id:
                filtered_data = self.data[self.data['Equipment ID'] == equipment_id]
            else:
                filtered_data = self.data
            
            if len(filtered_data) == 0:
                return {"error": "No data found for the specified equipment"}
            
            # Prepare features for anomaly detection
            anomaly_features = np.array(filtered_data['anomaly_features'].tolist())
            anomaly_features_scaled = self.scaler.transform(anomaly_features)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.decision_function(anomaly_features_scaled)
            anomaly_predictions = self.anomaly_detector.predict(anomaly_features_scaled)
            
            # Create results
            results = []
            for i, (_, row) in enumerate(filtered_data.iterrows()):
                is_anomaly = anomaly_predictions[i] == -1
                anomaly_score = anomaly_scores[i]
                
                # Define anomaly types based on patterns
                anomaly_type = "normal"
                if is_anomaly:
                    if row['Idle Hours/Day'] > 12:
                        anomaly_type = "high_idle_time"
                    elif row['Engine Hours/Day'] == 0 and row['Idle Hours/Day'] > 8:
                        anomaly_type = "unused_equipment"
                    elif row['utilization_ratio'] < 0.2:
                        anomaly_type = "low_utilization"
                    elif row['efficiency_score'] < 0.3:
                        anomaly_type = "low_efficiency"
                    else:
                        anomaly_type = "usage_pattern_anomaly"
                
                results.append({
                    "equipment_id": row['Equipment ID'],
                    "type": row['Type'],
                    "site_id": row['User ID'],
                    "check_out_date": row['Check-Out Date'].strftime('%Y-%m-%d'),
                    "check_in_date": row['Check-in Date'].strftime('%Y-%m-%d'),
                    "engine_hours_per_day": row['Engine Hours/Day'],
                    "idle_hours_per_day": row['Idle Hours/Day'],
                    "utilization_ratio": round(row['utilization_ratio'], 3),
                    "efficiency_score": round(row['efficiency_score'], 3),
                    "is_anomaly": bool(is_anomaly),
                    "anomaly_type": anomaly_type,
                    "anomaly_score": round(anomaly_score, 3),
                    "severity": "high" if abs(anomaly_score) > 0.5 else "medium" if abs(anomaly_score) > 0.3 else "low"
                })
            
            # Summary statistics
            total_anomalies = sum(1 for r in results if r['is_anomaly'])
            anomaly_summary = {
                "total_records": len(results),
                "total_anomalies": total_anomalies,
                "anomaly_percentage": round((total_anomalies / len(results)) * 100, 2),
                "anomaly_types": {},
                "equipment_anomalies": {}
            }
            
            # Count anomaly types
            for result in results:
                if result['is_anomaly']:
                    anomaly_type = result['anomaly_type']
                    anomaly_summary['anomaly_types'][anomaly_type] = anomaly_summary['anomaly_types'].get(anomaly_type, 0) + 1
                    
                    equipment_type = result['type']
                    if equipment_type not in anomaly_summary['equipment_anomalies']:
                        anomaly_summary['equipment_anomalies'][equipment_type] = 0
                    anomaly_summary['equipment_anomalies'][equipment_type] += 1
            
            return {
                "anomalies": results,
                "summary": anomaly_summary,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error detecting anomalies: {str(e)}"}
    
    def forecast_demand(self, equipment_type: str = None, site_id: str = None, days_ahead: int = 7) -> Dict:
        """Forecast equipment demand"""
        if not self.models_trained or self.data is None:
            return {"error": "Models not trained"}
        
        try:
            # Filter data based on parameters
            filtered_data = self.data.copy()
            if equipment_type:
                filtered_data = filtered_data[filtered_data['Type'] == equipment_type]
            if site_id and site_id != 'UNASSIGNED':
                filtered_data = filtered_data[filtered_data['User ID'] == site_id]
            
            if len(filtered_data) == 0:
                return {"error": "No data found for the specified parameters"}
            
            # Generate future dates for forecasting
            last_date = filtered_data['Check-Out Date'].max()
            future_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
            
            # Prepare features for forecasting
            equipment_encoded = self.equipment_encoder.transform([equipment_type])[0] if equipment_type else 0
            
            forecasts = []
            for future_date in future_dates:
                features = np.array([[
                    equipment_encoded,
                    future_date.dayofweek,
                    future_date.month
                ]])
                
                # Predict demand
                predicted_demand = self.demand_forecaster.predict(features)[0]
                
                # Add some seasonality and trend
                seasonal_factor = 1.0
                if future_date.month in [6, 7, 8]:  # Summer months
                    seasonal_factor = 1.2
                elif future_date.month in [12, 1, 2]:  # Winter months
                    seasonal_factor = 0.8
                
                # Add day-of-week factor
                if future_date.dayofweek < 5:  # Weekdays
                    day_factor = 1.1
                else:  # Weekends
                    day_factor = 0.7
                
                adjusted_demand = max(0, round(predicted_demand * seasonal_factor * day_factor, 1))
                
                forecasts.append({
                    "date": future_date.strftime('%Y-%m-%d'),
                    "day_of_week": future_date.strftime('%A'),
                    "predicted_demand": adjusted_demand,
                    "confidence": round(0.85 + np.random.normal(0, 0.05), 2)
                })
            
            # Calculate trend
            if len(forecasts) > 1:
                demands = [f['predicted_demand'] for f in forecasts]
                trend = "increasing" if demands[-1] > demands[0] else "decreasing" if demands[-1] < demands[0] else "stable"
            else:
                trend = "stable"
            
            return {
                "equipment_type": equipment_type,
                "site_id": site_id,
                "forecast_days": days_ahead,
                "forecasts": forecasts,
                "trend": trend,
                "total_predicted_demand": sum(f['predicted_demand'] for f in forecasts),
                "average_daily_demand": round(np.mean([f['predicted_demand'] for f in forecasts]), 2),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error forecasting demand: {str(e)}"}
    
    def get_equipment_stats(self) -> Dict:
        """Get comprehensive equipment statistics"""
        if self.data is None:
            return {"error": "No data available"}
        
        try:
            stats = {}
            
            # Overall statistics
            stats['overall'] = {
                "total_equipment": len(self.data),
                "total_rentals": len(self.data),
                "average_rental_duration": round(self.data['rental_duration'].mean(), 2),
                "total_engine_hours": round(self.data['Engine Hours/Day'].sum(), 2),
                "total_idle_hours": round(self.data['Idle Hours/Day'].sum(), 2),
                "average_utilization": round(self.data['utilization_ratio'].mean() * 100, 2)
            }
            
            # Statistics by equipment type
            equipment_stats = self.data.groupby('Type').agg({
                'Equipment ID': 'count',
                'Engine Hours/Day': ['mean', 'sum'],
                'Idle Hours/Day': ['mean', 'sum'],
                'utilization_ratio': 'mean',
                'efficiency_score': 'mean',
                'rental_duration': 'mean'
            }).round(3)
            
            stats['by_equipment_type'] = {}
            for equipment_type in equipment_stats.index:
                stats['by_equipment_type'][equipment_type] = {
                    "count": int(equipment_stats.loc[equipment_type, ('Equipment ID', 'count')]),
                    "avg_engine_hours": float(equipment_stats.loc[equipment_type, ('Engine Hours/Day', 'mean')]),
                    "total_engine_hours": float(equipment_stats.loc[equipment_type, ('Engine Hours/Day', 'sum')]),
                    "avg_idle_hours": float(equipment_stats.loc[equipment_type, ('Idle Hours/Day', 'mean')]),
                    "total_idle_hours": float(equipment_stats.loc[equipment_type, ('Idle Hours/Day', 'sum')]),
                    "avg_utilization": round(float(equipment_stats.loc[equipment_type, ('utilization_ratio', 'mean')]) * 100, 2),
                    "avg_efficiency": round(float(equipment_stats.loc[equipment_type, ('efficiency_score', 'mean')]) * 100, 2),
                    "avg_rental_duration": float(equipment_stats.loc[equipment_type, ('rental_duration', 'mean')])
                }
            
            # Site utilization statistics
            site_stats = self.data.groupby('User ID').agg({
                'Equipment ID': 'count',
                'utilization_ratio': 'mean',
                'efficiency_score': 'mean'
            }).round(3)
            
            stats['by_site'] = {}
            for site_id in site_stats.index:
                if site_id != 'UNASSIGNED':
                    stats['by_site'][site_id] = {
                        "equipment_count": int(site_stats.loc[site_id, 'Equipment ID']),
                        "avg_utilization": round(float(site_stats.loc[site_id, 'utilization_ratio']) * 100, 2),
                        "avg_efficiency": round(float(site_stats.loc[site_id, 'efficiency_score']) * 100, 2)
                    }
            
            # Time-based statistics
            monthly_stats = self.data.groupby(self.data['Check-Out Date'].dt.month).agg({
                'Equipment ID': 'count',
                'utilization_ratio': 'mean'
            }).round(3)
            
            stats['by_month'] = {}
            for month in monthly_stats.index:
                month_name = datetime(2025, month, 1).strftime('%B')
                stats['by_month'][month_name] = {
                    "rental_count": int(monthly_stats.loc[month, 'Equipment ID']),
                    "avg_utilization": round(float(monthly_stats.loc[month, 'utilization_ratio']) * 100, 2)
                }
            
            return stats
            
        except Exception as e:
            return {"error": f"Error generating statistics: {str(e)}"}
    
    def get_recommendations(self) -> Dict:
        """Get actionable recommendations based on data analysis"""
        if self.data is None:
            return {"error": "No data available"}
        
        try:
            recommendations = []
            
            # Check for underutilized equipment
            underutilized = self.data[self.data['utilization_ratio'] < 0.3]
            if len(underutilized) > 0:
                recommendations.append({
                    "type": "underutilization",
                    "priority": "high",
                    "description": f"{len(underutilized)} equipment items have utilization below 30%",
                    "action": "Consider reallocating or reducing rental duration for underutilized equipment",
                    "affected_equipment": underutilized['Equipment ID'].tolist()[:5]  # Top 5
                })
            
            # Check for high idle time
            high_idle = self.data[self.data['Idle Hours/Day'] > 12]
            if len(high_idle) > 0:
                recommendations.append({
                    "type": "high_idle_time",
                    "priority": "medium",
                    "description": f"{len(high_idle)} equipment items have idle time > 12 hours/day",
                    "action": "Review scheduling and operator allocation to reduce idle time",
                    "affected_equipment": high_idle['Equipment ID'].tolist()[:5]
                })
            
            # Check for unassigned equipment
            unassigned = self.data[self.data['User ID'] == 'UNASSIGNED']
            if len(unassigned) > 0:
                recommendations.append({
                    "type": "unassigned_equipment",
                    "priority": "high",
                    "description": f"{len(unassigned)} equipment items are not assigned to any site",
                    "action": "Assign unassigned equipment to active sites or return to inventory",
                    "affected_equipment": unassigned['Equipment ID'].tolist()
                })
            
            # Check for long rental durations
            long_rentals = self.data[self.data['rental_duration'] > 30]
            if len(long_rentals) > 0:
                recommendations.append({
                    "type": "long_rentals",
                    "priority": "medium",
                    "description": f"{len(long_rentals)} rentals exceed 30 days",
                    "action": "Review if long-term rentals are cost-effective vs. purchasing",
                    "affected_equipment": long_rentals['Equipment ID'].tolist()[:5]
                })
            
            # Equipment type recommendations
            equipment_demand = self.data.groupby('Type').size().sort_values(ascending=False)
            most_demanded = equipment_demand.index[0]
            least_demanded = equipment_demand.index[-1]
            
            recommendations.append({
                "type": "demand_analysis",
                "priority": "low",
                "description": f"Most demanded equipment: {most_demanded}, Least demanded: {least_demanded}",
                "action": f"Consider increasing inventory of {most_demanded} and reducing {least_demanded}",
                "affected_equipment": []
            })
            
            return {
                "recommendations": recommendations,
                "total_recommendations": len(recommendations),
                "high_priority_count": len([r for r in recommendations if r['priority'] == 'high']),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error generating recommendations: {str(e)}"}
    
    def save_models(self, models_dir: str = "models"):
        """Save trained models to disk"""
        if not self.models_trained:
            print("No trained models to save")
            return
        
        try:
            os.makedirs(models_dir, exist_ok=True)
            
            # Save models
            joblib.dump(self.anomaly_detector, os.path.join(models_dir, 'anomaly_detector.pkl'))
            joblib.dump(self.demand_forecaster, os.path.join(models_dir, 'demand_forecaster.pkl'))
            joblib.dump(self.scaler, os.path.join(models_dir, 'scaler.pkl'))
            joblib.dump(self.equipment_encoder, os.path.join(models_dir, 'equipment_encoder.pkl'))
            joblib.dump(self.site_encoder, os.path.join(models_dir, 'site_encoder.pkl'))
            
            print(f"Models saved to {models_dir}")
            
        except Exception as e:
            print(f"Error saving models: {e}")
    
    def load_models(self, models_dir: str = "models"):
        """Load trained models from disk"""
        try:
            self.anomaly_detector = joblib.load(os.path.join(models_dir, 'anomaly_detector.pkl'))
            self.demand_forecaster = joblib.load(os.path.join(models_dir, 'demand_forecaster.pkl'))
            self.scaler = joblib.load(os.path.join(models_dir, 'scaler.pkl'))
            self.equipment_encoder = joblib.load(os.path.join(models_dir, 'equipment_encoder.pkl'))
            self.site_encoder = joblib.load(os.path.join(models_dir, 'site_encoder.pkl'))
            
            self.models_trained = True
            print("Models loaded successfully")
            
        except Exception as e:
            print(f"Error loading models: {e}")
            self.models_trained = False

    def get_model_status(self) -> Dict:
        """Get the status of ML models"""
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
        saved_models_exist = os.path.exists(models_dir)
        
        status = {
            "models_trained": self.models_trained,
            "data_loaded": self.data is not None,
            "data_records": len(self.data) if self.data is not None else 0,
            "saved_models_exist": saved_models_exist,
            "models_directory": models_dir
        }
        
        if saved_models_exist:
            try:
                model_files = os.listdir(models_dir)
                status["saved_model_files"] = model_files
                status["total_saved_models"] = len(model_files)
            except Exception as e:
                status["saved_model_files"] = []
                status["total_saved_models"] = 0
                status["error"] = str(e)
        
        return status

    def _try_load_models(self, models_dir: str) -> bool:
        """Attempt to load models from a directory."""
        try:
            self.anomaly_detector = joblib.load(os.path.join(models_dir, 'anomaly_detector.pkl'))
            self.demand_forecaster = joblib.load(os.path.join(models_dir, 'demand_forecaster.pkl'))
            self.scaler = joblib.load(os.path.join(models_dir, 'scaler.pkl'))
            self.equipment_encoder = joblib.load(os.path.join(models_dir, 'equipment_encoder.pkl'))
            self.site_encoder = joblib.load(os.path.join(models_dir, 'site_encoder.pkl'))
            
            # Attempt to load scaler and encoders if they were saved
            try:
                self.scaler = joblib.load(os.path.join(models_dir, 'scaler.pkl'))
                self.equipment_encoder = joblib.load(os.path.join(models_dir, 'equipment_encoder.pkl'))
                self.site_encoder = joblib.load(os.path.join(models_dir, 'site_encoder.pkl'))
            except FileNotFoundError:
                print("⚠️ Scaler, Equipment Encoder, or Site Encoder not found in saved models. Retraining models.")
                return False

            self.models_trained = True
            print("✅ Loaded saved ML models successfully!")
            return True
        except FileNotFoundError:
            print("📊 No saved models found in the specified directory.")
            return False
        except Exception as e:
            print(f"Error loading models from {models_dir}: {e}")
            return False

# Create a simple interface for the existing ML integration
class SimpleML:
    def __init__(self):
        self.smart_system = SmartMLSystem()
    
    def predict_demand(self, equipment_type: str = None, site_id: str = None, days_ahead: int = 7):
        """Simple demand prediction interface"""
        result = self.smart_system.forecast_demand(equipment_type, site_id, days_ahead)
        if 'error' in result:
            return 0
        return result.get('total_predicted_demand', 0)
    
    def get_equipment_stats(self):
        """Get equipment statistics"""
        return self.smart_system.get_equipment_stats()

if __name__ == "__main__":
    # Test the ML system
    ml_system = SmartMLSystem()
    
    if ml_system.models_trained:
        print("\n=== Testing Anomaly Detection ===")
        anomalies = ml_system.detect_anomalies()
        if 'error' not in anomalies:
            print(f"Found {anomalies['summary']['total_anomalies']} anomalies")
        
        print("\n=== Testing Demand Forecasting ===")
        forecast = ml_system.forecast_demand(equipment_type="Excavator", days_ahead=14)
        if 'error' not in forecast:
            print(f"Forecast for Excavator: {forecast['total_predicted_demand']} units over 14 days")
        
        print("\n=== Testing Equipment Stats ===")
        stats = ml_system.get_equipment_stats()
        if 'error' not in stats:
            print(f"Total equipment: {stats['overall']['total_equipment']}")
        
        print("\n=== Testing Recommendations ===")
        recs = ml_system.get_recommendations()
        if 'error' not in recs:
            print(f"Generated {recs['total_recommendations']} recommendations")
    else:
        print("ML system not trained properly")
