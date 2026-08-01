from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys
import os

# Add the ml directory to the path (search several candidate locations)
_here = os.path.dirname(os.path.abspath(__file__))
_candidates = [
    os.path.join(_here, '..', '..', '..', 'ml'),   # repo root /ml
    os.path.join(_here, '..', '..', 'ml'),          # backend/ml
    os.path.join(os.getcwd(), 'ml'),
]
for _candidate in _candidates:
    _candidate = os.path.normpath(_candidate)
    if os.path.isdir(_candidate) and _candidate not in sys.path:
        sys.path.append(_candidate)

from app.database import get_db
from app import crud
from app import schemas

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# Lazy-load the ML system so cold starts that only hit /dashboard stay fast.
_ml_system = None
_ml_load_attempted = False

def _get_ml_system():
    global _ml_system, _ml_load_attempted
    if _ml_load_attempted:
        return _ml_system
    _ml_load_attempted = True
    try:
        from smart_ml_system import SmartMLSystem
        _ml_system = SmartMLSystem()
        print("Smart ML system loaded successfully!")
    except Exception as e:
        print(f"Warning: Smart ML system could not be loaded: {e}")
        _ml_system = None
    return _ml_system

def _ml_loaded() -> bool:
    return _get_ml_system() is not None

@router.get("/status")
def get_ml_status():
    """Get the status of ML models"""
    return {
        "models_loaded": _ml_loaded(),
        "demand_forecasting": "available" if _ml_loaded() else "unavailable",
        "anomaly_detection": "available" if _ml_loaded() else "unavailable",
        "recommendations": "available" if _ml_loaded() else "unavailable",
        "analytics": "available" if _ml_loaded() else "unavailable"
    }

@router.post("/demand-forecast")
def generate_demand_forecast(
    equipment_type: str = None,
    site_id: str = None,
    days_ahead: int = 7
):
    """Generate demand forecast for a specific site and equipment type"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Generate forecast using the smart ML system
        forecast = _get_ml_system().forecast_demand(
            equipment_type=equipment_type,
            site_id=site_id,
            days_ahead=days_ahead
        )
        
        if 'error' in forecast:
            raise HTTPException(
                status_code=400,
                detail=forecast['error']
            )
        
        return forecast
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating demand forecast: {str(e)}"
        )

@router.post("/demand-forecast/bulk")
def generate_bulk_demand_forecast(days_ahead: int = 7):
    """Generate demand forecasts for all equipment types"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Get equipment statistics to predict demand
        equipment_stats = _get_ml_system().get_equipment_stats()
        
        if 'error' in equipment_stats:
            raise HTTPException(
                status_code=400,
                detail=equipment_stats['error']
            )
        
        forecasts = []
        for equipment_type in equipment_stats['by_equipment_type'].keys():
            forecast = _get_ml_system().forecast_demand(
                equipment_type=equipment_type,
                days_ahead=days_ahead
            )
            
            if 'error' not in forecast:
                forecasts.append({
                    "equipment_type": equipment_type,
                    "predicted_demand": forecast['total_predicted_demand'],
                    "average_daily_demand": forecast['average_daily_demand'],
                    "trend": forecast['trend'],
                    "days_ahead": days_ahead
                })
        
        return {
            "message": f"Generated {len(forecasts)} demand forecasts",
            "forecasts": forecasts,
            "total_forecast_days": days_ahead,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating bulk demand forecast: {str(e)}"
        )

@router.post("/anomaly-detection")
def detect_anomalies(equipment_id: str = None):
    """Detect anomalies in equipment usage"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Detect anomalies using the smart ML system
        anomalies = _get_ml_system().detect_anomalies(equipment_id=equipment_id)
        
        if 'error' in anomalies:
            raise HTTPException(
                status_code=400,
                detail=anomalies['error']
            )
        
        return anomalies
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting anomalies: {str(e)}"
        )

@router.get("/anomaly-detection/summary")
def get_anomaly_summary():
    """Get a summary of all detected anomalies"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Get all anomalies
        anomalies = _get_ml_system().detect_anomalies()
        
        if 'error' in anomalies:
            raise HTTPException(
                status_code=400,
                detail=anomalies['error']
            )
        
        # Return just the summary
        return {
            "summary": anomalies['summary'],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting anomaly summary: {str(e)}"
        )

@router.get("/analytics/equipment-stats")
def get_equipment_statistics():
    """Get comprehensive equipment statistics and analytics"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Get equipment statistics
        stats = _get_ml_system().get_equipment_stats()
        
        if 'error' in stats:
            raise HTTPException(
                status_code=400,
                detail=stats['error']
            )
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting equipment statistics: {str(e)}"
        )

@router.get("/analytics/recommendations")
def get_recommendations():
    """Get actionable recommendations based on data analysis"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Get recommendations
        recommendations = _get_ml_system().get_recommendations()
        
        if 'error' in recommendations:
            raise HTTPException(
                status_code=400,
                detail=recommendations['error']
            )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )

@router.get("/analytics/equipment/{equipment_type}/performance")
def get_equipment_performance(equipment_type: str):
    """Get performance metrics for a specific equipment type"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Get equipment statistics
        stats = _get_ml_system().get_equipment_stats()
        
        if 'error' in stats:
            raise HTTPException(
                status_code=400,
                detail=stats['error']
            )
        
        # Filter for specific equipment type
        if equipment_type in stats['by_equipment_type']:
            equipment_stats = stats['by_equipment_type'][equipment_type]
            
            # Get demand forecast for this equipment type
            forecast = _get_ml_system().forecast_demand(
                equipment_type=equipment_type,
                days_ahead=30
            )
            
            return {
                "equipment_type": equipment_type,
                "current_stats": equipment_stats,
                "demand_forecast": forecast if 'error' not in forecast else None,
                "generated_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Equipment type '{equipment_type}' not found"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting equipment performance: {str(e)}"
        )

@router.get("/analytics/site/{site_id}/utilization")
def get_site_utilization(site_id: str):
    """Get utilization metrics for a specific site"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Get equipment statistics
        stats = _get_ml_system().get_equipment_stats()
        
        if 'error' in stats:
            raise HTTPException(
                status_code=400,
                detail=stats['error']
            )
        
        # Filter for specific site
        if site_id in stats['by_site']:
            site_stats = stats['by_site'][site_id]
            
            # Get demand forecast for this site
            forecast = _get_ml_system().forecast_demand(
                site_id=site_id,
                days_ahead=30
            )
            
            return {
                "site_id": site_id,
                "current_stats": site_stats,
                "demand_forecast": forecast if 'error' not in forecast else None,
                "generated_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Site '{site_id}' not found"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting site utilization: {str(e)}"
        )

@router.post("/models/save")
def save_ml_models():
    """Save the trained ML models to disk"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Save models
        _get_ml_system().save_models()
        
        return {
            "message": "ML models saved successfully",
            "models_saved": [
                "anomaly_detector.pkl",
                "demand_forecaster.pkl", 
                "scaler.pkl",
                "equipment_encoder.pkl",
                "site_encoder.pkl"
            ],
            "saved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving ML models: {str(e)}"
        )

@router.post("/models/retrain")
def retrain_ml_models():
    """Retrain the ML models with current data"""
    if not _ml_loaded():
        raise HTTPException(
            status_code=503, 
            detail="ML system is not available."
        )
    
    try:
        # Retrain models
        _get_ml_system()._train_models()
        
        if _get_ml_system().models_trained:
            return {
                "message": "ML models retrained successfully",
                "models_trained": True,
                "retrained_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrain ML models"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retraining ML models: {str(e)}"
        )

@router.get("/health")
def ml_health_check():
    """Health check for the ML system"""
    if _ml_loaded():
        model_status = _get_ml_system().get_model_status()
        return {
            "status": "healthy" if model_status["models_trained"] else "unhealthy",
            "ml_system_available": _ml_loaded(),
            "models_trained": model_status["models_trained"],
            "data_loaded": model_status["data_loaded"],
            "data_records": model_status["data_records"],
            "saved_models_exist": model_status["saved_models_exist"],
            "total_saved_models": model_status.get("total_saved_models", 0),
            "models_directory": model_status["models_directory"],
            "checked_at": datetime.now().isoformat()
        }
    else:
        return {
            "status": "unhealthy",
            "ml_system_available": _ml_loaded(),
            "models_trained": False,
            "data_loaded": False,
            "data_records": 0,
            "saved_models_exist": False,
            "total_saved_models": 0,
            "models_directory": None,
            "checked_at": datetime.now().isoformat()
        }
