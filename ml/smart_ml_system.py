import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
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
        self.demand_forecaster = GradientBoostingRegressor(
            n_estimators=200, 
            learning_rate=0.1, 
            max_depth=6, 
            random_state=42,
            subsample=0.8
        )
        self.site_specific_models = {}  # Store site-specific models
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
        """Preprocess the data for ML models with enhanced features"""
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
        
        # Enhanced feature engineering for demand forecasting
        self.data['month'] = self.data['Check-Out Date'].dt.month
        self.data['day_of_week'] = self.data['Check-Out Date'].dt.dayofweek
        self.data['quarter'] = self.data['Check-Out Date'].dt.quarter
        self.data['is_weekend'] = self.data['day_of_week'].isin([5, 6]).astype(int)
        
        # Seasonal factors based on construction industry patterns
        self.data['seasonal_factor'] = 1.0  # Default fall moderate
        self.data.loc[self.data['month'].isin([6, 7, 8]), 'seasonal_factor'] = 1.3  # Summer peak
        self.data.loc[self.data['month'].isin([12, 1, 2]), 'seasonal_factor'] = 0.7  # Winter low
        self.data.loc[self.data['month'].isin([3, 4, 5]), 'seasonal_factor'] = 1.1  # Spring moderate
        
        # Site-specific features
        self.data['site_equipment_count'] = self.data.groupby('User ID')['Equipment ID'].transform('count')
        self.data['site_avg_utilization'] = self.data.groupby('User ID')['utilization_ratio'].transform('mean')
        
        # Equipment type popularity by site
        self.data['equipment_site_popularity'] = self.data.groupby(['User ID', 'Type'])['Equipment ID'].transform('count')
        
        # Encode categorical variables
        self.data['equipment_type_encoded'] = self.equipment_encoder.fit_transform(self.data['Type'])
        
        # Handle NULL values in User ID (which represents site assignment)
        self.data['User ID'] = self.data['User ID'].fillna('UNASSIGNED')
        self.data['site_encoded'] = self.site_encoder.fit_transform(self.data['User ID'])
        
        # Create demand features for forecasting
        self._create_demand_features()
    
    def _create_demand_features(self):
        """Create features specifically for demand forecasting"""
        # Daily demand aggregation by site and equipment type
        daily_demand = self.data.groupby(['User ID', 'Type', 'Check-Out Date']).size().reset_index(name='daily_demand')
        daily_demand['month'] = daily_demand['Check-Out Date'].dt.month
        daily_demand['day_of_week'] = daily_demand['Check-Out Date'].dt.dayofweek
        daily_demand['quarter'] = daily_demand['Check-Out Date'].dt.quarter
        
        # Calculate rolling averages for demand patterns
        daily_demand = daily_demand.sort_values(['User ID', 'Type', 'Check-Out Date'])
        daily_demand['demand_7d_avg'] = daily_demand.groupby(['User ID', 'Type'])['daily_demand'].rolling(7, min_periods=1).mean().reset_index(0, drop=True).values
        daily_demand['demand_30d_avg'] = daily_demand.groupby(['User ID', 'Type'])['daily_demand'].rolling(30, min_periods=1).mean().reset_index(0, drop=True).values
        
        # Merge back to main data
        self.data = self.data.merge(
            daily_demand[['User ID', 'Type', 'Check-Out Date', 'daily_demand', 'demand_7d_avg', 'demand_30d_avg']], 
            on=['User ID', 'Type', 'Check-Out Date'], 
            how='left'
        )
        
        # Fill NaN values
        self.data['daily_demand'] = self.data['daily_demand'].fillna(0)
        self.data['demand_7d_avg'] = self.data['demand_7d_avg'].fillna(0)
        self.data['demand_30d_avg'] = self.data['demand_30d_avg'].fillna(0)
    
    def _train_models(self):
        """Train ML models with enhanced features"""
        if self.data is None or len(self.data) < 50:
            print("⚠️ Insufficient data for training models")
            return
        
        try:
            print("🔄 Training ML models...")
            
            # Prepare features for demand forecasting
            feature_columns = [
                'equipment_type_encoded', 'site_encoded', 'month', 'day_of_week', 
                'quarter', 'is_weekend', 'seasonal_factor', 'site_equipment_count',
                'site_avg_utilization', 'equipment_site_popularity', 'demand_7d_avg',
                'demand_30d_avg', 'rental_duration', 'utilization_ratio'
            ]
            
            # Remove rows with NaN values
            clean_data = self.data.dropna(subset=feature_columns)
            
            if len(clean_data) < 30:
                print("⚠️ Insufficient clean data for training")
                return
            
            X = clean_data[feature_columns].values
            y = clean_data['daily_demand'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train demand forecaster
            print("📈 Training demand forecaster...")
            self.demand_forecaster.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.demand_forecaster.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"✅ Demand forecaster trained successfully!")
            print(f"   MSE: {mse:.4f}")
            print(f"   MAE: {mae:.4f}")
            print(f"   R²: {r2:.4f}")
            
            # Train site-specific models for better accuracy
            self._train_site_specific_models()
            
            # Train anomaly detector
            print("🔍 Training anomaly detector...")
            anomaly_features = ['Engine Hours/Day', 'Idle Hours/Day', 'utilization_ratio', 'efficiency_score']
            anomaly_data = clean_data[anomaly_features].dropna()
            
            if len(anomaly_data) > 0:
                self.anomaly_detector.fit(anomaly_data)
                print("✅ Anomaly detector trained successfully!")
            
            self.models_trained = True
            
        except Exception as e:
            print(f"❌ Error training models: {e}")
            self.models_trained = False
    
    def _train_site_specific_models(self):
        """Train separate models for each site to improve accuracy"""
        print("🏗️ Training site-specific models...")
        
        # Get unique sites
        sites = self.data['User ID'].unique()
        
        for site in sites:
            if site == 'UNASSIGNED':
                continue
                
            site_data = self.data[self.data['User ID'] == site]
            if len(site_data) < 10:  # Need minimum data for site-specific model
                continue
            
            try:
                # Prepare site-specific features
                feature_columns = [
                    'equipment_type_encoded', 'month', 'day_of_week', 'quarter',
                    'is_weekend', 'seasonal_factor', 'demand_7d_avg', 'demand_30d_avg'
                ]
                
                site_features = site_data[feature_columns].dropna()
                site_target = site_data.loc[site_features.index, 'daily_demand']
                
                if len(site_features) < 5:
                    continue
                
                # Train site-specific model
                site_model = GradientBoostingRegressor(
                    n_estimators=100, 
                    learning_rate=0.1, 
                    max_depth=4, 
                    random_state=42
                )
                
                site_model.fit(site_features, site_target)
                self.site_specific_models[site] = site_model
                
            except Exception as e:
                print(f"⚠️ Could not train model for site {site}: {e}")
        
        print(f"✅ Trained {len(self.site_specific_models)} site-specific models")
    
    def detect_anomalies(self, equipment_id: str = None) -> Dict:
        """Detect anomalies in equipment usage"""
        if not self.models_trained or self.data is None:
            return {"error": "Models not trained"}
        
        try:
            # Prepare features for anomaly detection
            if equipment_id:
                equipment_data = self.data[self.data['Equipment ID'] == equipment_id]
                if len(equipment_data) == 0:
                    return {"error": f"Equipment {equipment_id} not found"}
            else:
                equipment_data = self.data
            
            # Select features for anomaly detection
            anomaly_features = ['Engine Hours/Day', 'Idle Hours/Day', 'utilization_ratio', 'efficiency_score']
            feature_data = equipment_data[anomaly_features].dropna()
            
            if len(feature_data) == 0:
                return {"error": "No valid data for anomaly detection"}
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.decision_function(feature_data)
            anomaly_predictions = self.anomaly_detector.predict(feature_data)
            
            # Find anomalous records
            anomalous_indices = np.where(anomaly_predictions == -1)[0]
            anomalies = []
            
            for idx in anomalous_indices:
                record = equipment_data.iloc[feature_data.index[idx]]
                anomalies.append({
                    "equipment_id": record['Equipment ID'],
                    "equipment_type": record['Type'],
                    "site_id": record['User ID'],
                    "anomaly_score": float(anomaly_scores[idx]),
                    "engine_hours": float(record['Engine Hours/Day']),
                    "idle_hours": float(record['Idle Hours/Day']),
                    "utilization": float(record['utilization_ratio']),
                    "efficiency": float(record['efficiency_score'])
                })
            
            # Summary statistics
            anomaly_summary = {
                "total_anomalies": len(anomalies),
                "anomaly_rate": len(anomalies) / len(feature_data) * 100,
                "equipment_affected": len(set([a['equipment_id'] for a in anomalies])),
                "sites_affected": len(set([a['site_id'] for a in anomalies if a['site_id'] != 'UNASSIGNED']))
            }
            
            return {
                "anomalies": anomalies,
                "summary": anomaly_summary,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error detecting anomalies: {str(e)}"}
    
    def forecast_demand(self, equipment_type: str = None, site_id: str = None, days_ahead: int = 30) -> Dict:
        """Enhanced demand forecasting with site-specific predictions"""
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
            
            forecasts = []
            total_predicted_demand = 0
            
            for i, future_date in enumerate(future_dates):
                # Prepare features for prediction
                features = self._prepare_forecast_features(
                    equipment_type, site_id, future_date, filtered_data
                )
                
                # Use site-specific model if available, otherwise use global model
                if site_id and site_id in self.site_specific_models and equipment_type:
                    # Use site-specific model
                    site_features = features[:8]  # Site-specific features only
                    predicted_demand = self.site_specific_models[site_id].predict([site_features])[0]
                else:
                    # Use global model
                    features_scaled = self.scaler.transform([features])
                    predicted_demand = self.demand_forecaster.predict(features_scaled)[0]
                
                # Apply realistic constraints and adjustments
                predicted_demand = self._apply_realistic_constraints(
                    predicted_demand, future_date, filtered_data, equipment_type, site_id
                )
                
                # Calculate confidence based on data availability and model performance
                confidence = self._calculate_forecast_confidence(
                    filtered_data, equipment_type, site_id, future_date
                )
                
                forecast = {
                    "date": future_date.strftime('%Y-%m-%d'),
                    "day_of_week": future_date.strftime('%A'),
                    "predicted_demand": round(max(0, predicted_demand), 1),
                    "confidence": round(confidence, 2)
                }
                
                forecasts.append(forecast)
                total_predicted_demand += forecast['predicted_demand']
            
            # Calculate trend and insights
            trend, trend_strength = self._calculate_demand_trend(forecasts)
            
            return {
                "equipment_type": equipment_type,
                "site_id": site_id,
                "forecast_days": days_ahead,
                "forecasts": forecasts,
                "trend": trend,
                "trend_strength": trend_strength,
                "total_predicted_demand": round(total_predicted_demand, 1),
                "average_daily_demand": round(total_predicted_demand / days_ahead, 1),
                "peak_demand_day": max(forecasts, key=lambda x: x['predicted_demand']),
                "low_demand_day": min(forecasts, key=lambda x: x['predicted_demand']),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error forecasting demand: {str(e)}"}
    
    def _prepare_forecast_features(self, equipment_type: str, site_id: str, future_date: datetime, filtered_data: pd.DataFrame) -> List[float]:
        """Prepare features for demand forecasting"""
        # Equipment type encoding
        equipment_encoded = self.equipment_encoder.transform([equipment_type])[0] if equipment_type else 0
        
        # Site encoding
        site_encoded = self.site_encoder.transform([site_id])[0] if site_id else 0
        
        # Time-based features
        month = future_date.month
        day_of_week = future_date.dayofweek
        quarter = future_date.quarter
        is_weekend = 1 if day_of_week in [5, 6] else 0
        
        # Seasonal factor
        seasonal_factor = 1.3 if month in [6, 7, 8] else 0.7 if month in [12, 1, 2] else 1.1 if month in [3, 4, 5] else 1.0
        
        # Site-specific features
        site_equipment_count = filtered_data['site_equipment_count'].iloc[0] if len(filtered_data) > 0 else 0
        site_avg_utilization = filtered_data['site_avg_utilization'].iloc[0] if len(filtered_data) > 0 else 0.5
        
        # Equipment popularity
        equipment_site_popularity = filtered_data['equipment_site_popularity'].iloc[0] if len(filtered_data) > 0 else 1
        
        # Demand averages (use recent data if available)
        demand_7d_avg = filtered_data['demand_7d_avg'].iloc[-1] if len(filtered_data) > 0 else 0
        demand_30d_avg = filtered_data['demand_30d_avg'].iloc[-1] if len(filtered_data) > 0 else 0
        
        # Additional features
        rental_duration = filtered_data['rental_duration'].mean() if len(filtered_data) > 0 else 30
        utilization_ratio = filtered_data['utilization_ratio'].mean() if len(filtered_data) > 0 else 0.5
        
        return [
            equipment_encoded, site_encoded, month, day_of_week, quarter, is_weekend,
            seasonal_factor, site_equipment_count, site_avg_utilization, 
            equipment_site_popularity, demand_7d_avg, demand_30d_avg,
            rental_duration, utilization_ratio
        ]
    
    def _apply_realistic_constraints(self, predicted_demand: float, future_date: datetime, 
                                   filtered_data: pd.DataFrame, equipment_type: str, site_id: str) -> float:
        """Apply realistic constraints to demand predictions"""
        # Base constraints
        min_demand = 0
        max_demand = 20  # Maximum reasonable daily demand
        
        # Site-specific constraints
        if site_id and site_id != 'UNASSIGNED':
            site_equipment = filtered_data[filtered_data['User ID'] == site_id]
            if len(site_equipment) > 0:
                max_demand = min(max_demand, len(site_equipment) * 2)  # Can't exceed 2x available equipment
        
        # Equipment type constraints
        if equipment_type:
            equipment_data = filtered_data[filtered_data['Type'] == equipment_type]
            if len(equipment_data) > 0:
                max_demand = min(max_demand, len(equipment_data) * 1.5)
        
        # Day-of-week constraints
        if future_date.weekday() >= 5:  # Weekend
            predicted_demand *= 0.6  # Reduce weekend demand
        
        # Seasonal constraints
        if future_date.month in [12, 1, 2]:  # Winter
            predicted_demand *= 0.8  # Reduce winter demand
        
        # Apply constraints
        predicted_demand = max(min_demand, min(max_demand, predicted_demand))
        
        return predicted_demand
    
    def _calculate_forecast_confidence(self, filtered_data: pd.DataFrame, equipment_type: str, 
                                     site_id: str, future_date: datetime) -> float:
        """Calculate confidence score for forecast"""
        base_confidence = 0.7
        
        # Data availability factor
        data_points = len(filtered_data)
        if data_points >= 100:
            data_factor = 1.0
        elif data_points >= 50:
            data_factor = 0.9
        elif data_points >= 20:
            data_factor = 0.8
        else:
            data_factor = 0.6
        
        # Site-specific factor
        site_factor = 1.0
        if site_id and site_id != 'UNASSIGNED':
            site_data = filtered_data[filtered_data['User ID'] == site_id]
            if len(site_data) >= 10:
                site_factor = 1.0
            elif len(site_data) >= 5:
                site_factor = 0.9
            else:
                site_factor = 0.7
        
        # Equipment type factor
        equipment_factor = 1.0
        if equipment_type:
            equipment_data = filtered_data[filtered_data['Type'] == equipment_type]
            if len(equipment_data) >= 20:
                equipment_factor = 1.0
            elif len(equipment_data) >= 10:
                equipment_factor = 0.9
            else:
                equipment_factor = 0.8
        
        # Time distance factor (closer dates have higher confidence)
        days_from_last = (future_date - filtered_data['Check-Out Date'].max()).days
        time_factor = max(0.5, 1.0 - (days_from_last * 0.01))
        
        # Calculate final confidence
        confidence = base_confidence * data_factor * site_factor * equipment_factor * time_factor
        
        return min(0.95, max(0.3, confidence))  # Clamp between 0.3 and 0.95
    
    def _calculate_demand_trend(self, forecasts: List[Dict]) -> Tuple[str, float]:
        """Calculate demand trend and strength"""
        if len(forecasts) < 2:
            return "stable", 0.0
        
        demands = [f['predicted_demand'] for f in forecasts]
        
        # Calculate trend using linear regression
        x = np.arange(len(demands))
        y = np.array(demands)
        
        if len(set(y)) == 1:  # All values are the same
            return "stable", 0.0
        
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate trend strength (R²)
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.1:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return trend, round(r_squared, 3)
    
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
                    "avg_efficiency": round(float(equipment_stats.loc[equipment_type, ('efficiency_score', 'mean')]), 3),
                    "avg_rental_duration": round(float(equipment_stats.loc[equipment_type, ('rental_duration', 'mean')]), 2)
                }
            
            # Statistics by site
            site_stats = self.data.groupby('User ID').agg({
                'Equipment ID': 'count',
                'Engine Hours/Day': ['mean', 'sum'],
                'Idle Hours/Day': ['mean', 'sum'],
                'utilization_ratio': 'mean',
                'efficiency_score': 'mean',
                'rental_duration': 'mean'
            }).round(3)
            
            stats['by_site'] = {}
            for site in site_stats.index:
                if site != 'UNASSIGNED':
                    stats['by_site'][site] = {
                        "equipment_count": int(site_stats.loc[site, ('Equipment ID', 'count')]),
                        "avg_engine_hours": float(site_stats.loc[site, ('Engine Hours/Day', 'mean')]),
                        "total_engine_hours": float(site_stats.loc[site, ('Engine Hours/Day', 'sum')]),
                        "avg_idle_hours": float(site_stats.loc[site, ('Idle Hours/Day', 'mean')]),
                        "total_idle_hours": float(site_stats.loc[site, ('Idle Hours/Day', 'sum')]),
                        "avg_utilization": round(float(site_stats.loc[site, ('utilization_ratio', 'mean')]) * 100, 2),
                        "avg_efficiency": round(float(site_stats.loc[site, ('efficiency_score', 'mean')]), 3),
                        "avg_rental_duration": round(float(site_stats.loc[site, ('rental_duration', 'mean')]), 2)
                    }
            
            return stats
            
        except Exception as e:
            return {"error": f"Error getting equipment stats: {str(e)}"}
    
    def get_recommendations(self) -> Dict:
        """Get actionable recommendations based on data analysis"""
        if self.data is None:
            return {"error": "No data available"}
        
        try:
            recommendations = []
            
            # Analyze utilization patterns
            low_utilization = self.data[self.data['utilization_ratio'] < 0.3]
            if len(low_utilization) > 0:
                recommendations.append({
                    "type": "utilization",
                    "priority": "medium",
                    "title": "Low Equipment Utilization",
                    "description": f"{len(low_utilization)} equipment items have utilization below 30%",
                    "action": "Consider reallocating underutilized equipment or adjusting rental rates"
                })
            
            # Analyze rental duration patterns
            long_rentals = self.data[self.data['rental_duration'] > 60]
            if len(long_rentals) > 0:
                recommendations.append({
                    "type": "duration",
                    "priority": "low",
                    "title": "Long-term Rentals",
                    "description": f"{len(long_rentals)} rentals exceed 60 days",
                    "action": "Evaluate if long-term rentals are optimal for your business model"
                })
            
            # Analyze site distribution
            site_counts = self.data['User ID'].value_counts()
            if len(site_counts) > 0:
                most_active_site = site_counts.index[0]
                if site_counts.iloc[0] > len(self.data) * 0.3:  # More than 30% of activity
                    recommendations.append({
                        "type": "distribution",
                        "priority": "medium",
                        "title": "Site Concentration",
                        "description": f"Site {most_active_site} accounts for {site_counts.iloc[0]} rentals",
                        "action": "Consider diversifying operations across more sites"
                    })
            
            return {
                "recommendations": recommendations,
                "total_recommendations": len(recommendations),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error getting recommendations: {str(e)}"}
    
    def save_models(self):
        """Save trained models to disk"""
        models_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        try:
            joblib.dump(self.anomaly_detector, os.path.join(models_dir, 'anomaly_detector.pkl'))
            joblib.dump(self.demand_forecaster, os.path.join(models_dir, 'demand_forecaster.pkl'))
            joblib.dump(self.scaler, os.path.join(models_dir, 'scaler.pkl'))
            joblib.dump(self.equipment_encoder, os.path.join(models_dir, 'equipment_encoder.pkl'))
            joblib.dump(self.site_encoder, os.path.join(models_dir, 'site_encoder.pkl'))
            
            # Save site-specific models
            for site, model in self.site_specific_models.items():
                joblib.dump(model, os.path.join(models_dir, f'site_model_{site}.pkl'))
            
            print(f"Models saved to {models_dir}")
            
        except Exception as e:
            print(f"Error saving models: {e}")
    
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
            
            # Attempt to load site-specific models
            for site in self.site_specific_models.keys():
                try:
                    model_path = os.path.join(models_dir, f'site_model_{site}.pkl')
                    if os.path.exists(model_path):
                        self.site_specific_models[site] = joblib.load(model_path)
                        print(f"Loaded site-specific model for site {site}")
                    else:
                        print(f"⚠️ Site-specific model for site {site} not found. Retraining.")
                        self.site_specific_models[site] = None # Indicate retraining needed
                except Exception as e:
                    print(f"⚠️ Error loading site-specific model for site {site}: {e}")
                    self.site_specific_models[site] = None # Indicate retraining needed

            self.models_trained = True
            print("✅ Loaded saved ML models successfully!")
            return True
        except FileNotFoundError:
            print("📊 No saved models found in the specified directory.")
            return False
        except Exception as e:
            print(f"Error loading models from {models_dir}: {e}")
            return False

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
