from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import os
from . import models
from . import schemas
from . import crud
from .database import engine, get_db
from .routers import ml_integration, equipment, rentals, analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Rental Tracking System",
    description="API for tracking construction and mining equipment rentals with ML-powered demand forecasting and anomaly detection",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Start the Smart Rental Tracker"""
    logger.info("🚀 Starting Smart Rental Tracker...")
    logger.info("✅ System is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the Smart Rental Tracker"""
    logger.info("🛑 Stopping Smart Rental Tracker...")
    logger.info("✅ System stopped")

# Add CORS middleware
allowed_origins = [
    "http://localhost:3000",  # Next.js default port
    "https://smart-rental-tracker-frontend.onrender.com",  # Render frontend
    "https://smart-rental-tracker.vercel.app",  # Vercel frontend
    "https://smart-rental-tracker-git-main-vanshsehgal08s-projects.vercel.app",  # Vercel preview
    "https://smart-rental-tracker-con1tncjq-vanshsehgal08s-projects.vercel.app",  # Vercel preview
]

# Add environment variable origins
env_origins = os.getenv("ALLOWED_ORIGINS", "")
if env_origins:
    allowed_origins.extend([origin.strip() for origin in env_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ml_integration.router)
app.include_router(equipment.router)
app.include_router(rentals.router)
app.include_router(analytics.router)


@app.get("/")
def read_root():
    return {"message": "Smart Rental Tracking System API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint for Render monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "service": "Smart Rental Tracker API",
        "version": "1.0.0"
    }


@app.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    """Get dashboard overview data from database"""
    try:
        # Get all equipment from database
        equipment_list = crud.get_equipment_list(db, limit=1000)
        
        if not equipment_list:
            return {
                "overview": {
                    "total_equipment": 0,
                    "active_rentals": 0,
                    "anomalies": 0,
                    "utilization_rate": 0
                },
                "equipment_stats": {},
                "anomalies": {"summary": {"total_anomalies": 0}, "anomalies": []},
                "recommendations": ["No equipment data available"]
            }
        
        # Calculate statistics from database data
        total_equipment = len(equipment_list)
        active_rentals = len([eq for eq in equipment_list if eq.site_id])
        total_engine_hours = sum([eq.engine_hours_per_day or 0 for eq in equipment_list])
        total_idle_hours = sum([eq.idle_hours_per_day or 0 for eq in equipment_list])
        
        utilization_rate = 0
        if total_engine_hours + total_idle_hours > 0:
            utilization_rate = round((total_engine_hours / (total_engine_hours + total_idle_hours) * 100), 1)
        
        # Calculate anomalies based on database data
        anomalies = []
        anomaly_count = 0
        
        for eq in equipment_list:
            engine_hours = eq.engine_hours_per_day or 0
            idle_hours = eq.idle_hours_per_day or 0
            total_hours = engine_hours + idle_hours
            
            if total_hours > 0:
                utilization = engine_hours / total_hours
                
                # Detect anomalies
                if idle_hours > engine_hours * 1.5:  # High idle time
                    anomaly_count += 1
                    anomalies.append({
                        "equipment_id": eq.equipment_id,
                        "type": eq.type,
                        "anomaly_type": "high_idle_time",
                        "severity": "high" if idle_hours > engine_hours * 2 else "medium",
                        "anomaly_score": round(idle_hours / total_hours, 2),
                        "site_id": eq.site_id or "Unassigned",
                        "engine_hours_per_day": engine_hours,
                        "idle_hours_per_day": idle_hours,
                        "utilization_ratio": utilization,
                        "check_out_date": eq.check_out_date,
                        "check_in_date": eq.check_in_date
                    })
                elif utilization < 0.3:  # Low utilization
                    anomaly_count += 1
                    anomalies.append({
                        "equipment_id": eq.equipment_id,
                        "type": eq.type,
                        "anomaly_type": "low_utilization",
                        "severity": "medium" if utilization < 0.2 else "low",
                        "anomaly_score": round(1 - utilization, 2),
                        "site_id": eq.site_id or "Unassigned",
                        "engine_hours_per_day": engine_hours,
                        "idle_hours_per_day": idle_hours,
                        "utilization_ratio": utilization,
                        "check_out_date": eq.check_out_date,
                        "check_in_date": eq.check_in_date
                    })
        
        # Equipment type statistics
        equipment_stats = {
            "overview": {
                "total_equipment": total_equipment,
                "total_rentals": active_rentals,
                "average_utilization": utilization_rate,
                "total_engine_hours": round(total_engine_hours, 1)
            },
            "by_equipment_type": {}
        }
        
        # Calculate stats by equipment type
        equipment_types = {}
        for eq in equipment_list:
            eq_type = eq.type.lower()
            if eq_type not in equipment_types:
                equipment_types[eq_type] = []
            equipment_types[eq_type].append(eq)
        
        for equipment_type, type_equipment in equipment_types.items():
            type_engine_hours = sum([eq.engine_hours_per_day or 0 for eq in type_equipment])
            type_idle_hours = sum([eq.idle_hours_per_day or 0 for eq in type_equipment])
            type_total_hours = type_engine_hours + type_idle_hours
            
            type_utilization = 0
            if type_total_hours > 0:
                type_utilization = round((type_engine_hours / type_total_hours * 100), 1)
            
            equipment_stats["by_equipment_type"][equipment_type] = {
                "count": len(type_equipment),
                "utilization": type_utilization,
                "avg_utilization": type_utilization,
                "avg_efficiency": round(type_utilization / 100, 2)
            }
        
        # Generate recommendations based on database data
        recommendations = []
        if anomaly_count > 0:
            recommendations.append(f"Address {anomaly_count} equipment anomalies to improve utilization")
        
        low_utilization_types = [k for k, v in equipment_stats["by_equipment_type"].items() if v["utilization"] < 60]
        if low_utilization_types:
            recommendations.append(f"Focus on improving utilization for {', '.join(low_utilization_types)} equipment")
        
        if not recommendations:
            recommendations.append("All equipment types are performing well")
        
        return {
            "overview": {
                "total_equipment": total_equipment,
                "active_rentals": active_rentals,
                "anomalies": anomaly_count,
                "utilization_rate": utilization_rate
            },
            "equipment_stats": equipment_stats,
            "anomalies": {
                "summary": {
                    "total_anomalies": anomaly_count,
                    "total_records": total_equipment,
                    "anomaly_types": {
                        "high_idle_time": len([a for a in anomalies if a["anomaly_type"] == "high_idle_time"]),
                        "low_utilization": len([a for a in anomalies if a["anomaly_type"] == "low_utilization"])
                    }
                },
                "anomalies": anomalies
            },
            "recommendations": recommendations
        }
    
    except Exception as e:
        print(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Error getting dashboard data")


@app.get("/equipment-stats")
def get_equipment_stats(db: Session = Depends(get_db)):
    """Get statistics about the equipment data from database"""
    try:
        equipment_list = crud.get_equipment_list(db, limit=1000)
        
        if not equipment_list:
            return {"error": "No equipment data available"}
        
        # Basic stats
        total_records = len(equipment_list)
        equipment_types = {}
        total_engine_hours = 0
        total_idle_hours = 0
        records_with_sites = 0
        records_with_operators = 0
        
        for eq in equipment_list:
            # Count by type
            if eq.type in equipment_types:
                equipment_types[eq.type] += 1
            else:
                equipment_types[eq.type] = 1
            
            # Sum hours
            total_engine_hours += eq.engine_hours_per_day or 0
            total_idle_hours += eq.idle_hours_per_day or 0
            
            # Count assignments
            if eq.site_id:
                records_with_sites += 1
            if eq.last_operator_id:
                records_with_operators += 1
        
        avg_engine_hours = total_engine_hours / total_records if total_records > 0 else 0
        avg_idle_hours = total_idle_hours / total_records if total_records > 0 else 0
        avg_utilization = 0
        
        if total_engine_hours + total_idle_hours > 0:
            avg_utilization = (total_engine_hours / (total_engine_hours + total_idle_hours)) * 100
        
        return {
            "summary": {
                "total_records": total_records,
                "total_engine_hours": round(total_engine_hours, 1),
                "total_idle_hours": round(total_idle_hours, 1),
                "average_engine_hours_per_day": round(avg_engine_hours, 1),
                "average_idle_hours_per_day": round(avg_idle_hours, 1),
                "average_utilization_percentage": round(avg_utilization, 1)
            },
            "equipment_types": equipment_types,
            "assignments": {
                "records_with_sites": records_with_sites,
                "records_without_sites": total_records - records_with_sites,
                "records_with_operators": records_with_operators,
                "records_without_operators": total_records - records_with_operators
            }
        }
    
    except Exception as e:
        print(f"Error getting equipment stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting equipment statistics")


# Equipment endpoints
@app.post("/equipment/", response_model=schemas.Equipment)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    db_equipment = crud.get_equipment_by_equipment_id(db, equipment_id=equipment.equipment_id)
    if db_equipment:
        raise HTTPException(status_code=400, detail="Equipment ID already registered")
    return crud.create_equipment(db=db, equipment=equipment)


@app.get("/equipment/")
def read_equipment(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    """Get equipment from database"""
    try:
        equipment = crud.get_equipment_list(db, skip=skip, limit=limit)
        return equipment
    except Exception as e:
        print(f"Error reading equipment: {e}")
        raise HTTPException(status_code=500, detail="Error reading equipment data")


@app.get("/equipment/{equipment_id}", response_model=schemas.Equipment)
def read_equipment_by_id(equipment_id: int, db: Session = Depends(get_db)):
    db_equipment = crud.get_equipment(db, equipment_id=equipment_id)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return db_equipment


@app.put("/equipment/{equipment_id}", response_model=schemas.Equipment)
def update_equipment(equipment_id: int, equipment_update: schemas.EquipmentUpdate, db: Session = Depends(get_db)):
    db_equipment = crud.update_equipment(db, equipment_id=equipment_id, equipment_update=equipment_update)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return db_equipment


@app.get("/equipment/status/detailed", response_model=List[schemas.EquipmentWithStatus])
def read_equipment_with_status(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    return crud.get_equipment_with_status(db, skip=skip, limit=limit)


@app.get("/equipment/all")
def read_all_equipment(db: Session = Depends(get_db)):
    """Get all equipment from database without pagination limits"""
    try:
        equipment = crud.get_equipment_list(db, skip=0, limit=10000)  # Very high limit to get all
        return equipment
    except Exception as e:
        print(f"Error reading all equipment: {e}")
        raise HTTPException(status_code=500, detail="Error reading equipment data")


@app.get("/equipment/count")
def get_equipment_count(db: Session = Depends(get_db)):
    """Get total count of equipment in database"""
    try:
        count = db.query(models.Equipment).count()
        return {"total_equipment": count}
    except Exception as e:
        print(f"Error counting equipment: {e}")
        raise HTTPException(status_code=500, detail="Error counting equipment")


# Site endpoints
@app.post("/sites/", response_model=schemas.Site)
def create_site(site: schemas.SiteCreate, db: Session = Depends(get_db)):
    db_site = crud.get_site_by_site_id(db, site_id=site.site_id)
    if db_site:
        raise HTTPException(status_code=400, detail="Site ID already registered")
    return crud.create_site(db=db, site=site)


@app.get("/sites/", response_model=List[schemas.Site])
def read_sites(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sites = crud.get_sites(db, skip=skip, limit=limit)
    return sites


@app.get("/sites/{site_id}", response_model=schemas.Site)
def read_site(site_id: int, db: Session = Depends(get_db)):
    db_site = crud.get_site(db, site_id=site_id)
    if db_site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    return db_site


# Operator endpoints
@app.post("/operators/", response_model=schemas.Operator)
def create_operator(operator: schemas.OperatorCreate, db: Session = Depends(get_db)):
    db_operator = crud.get_operator_by_operator_id(db, operator_id=operator.operator_id)
    if db_operator:
        raise HTTPException(status_code=400, detail="Operator ID already registered")
    return crud.create_operator(db=db, operator=operator)


@app.get("/operators/", response_model=List[schemas.Operator])
def read_operators(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    operators = crud.get_operators(db, skip=skip, limit=limit)
    return operators


@app.get("/operators/{operator_id}", response_model=schemas.Operator)
def read_operator(operator_id: int, db: Session = Depends(get_db)):
    db_operator = crud.get_operator(db, operator_id=operator_id)
    if db_operator is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return db_operator


@app.put("/operators/{operator_id}", response_model=schemas.Operator)
def update_operator(operator_id: int, operator_update: schemas.OperatorUpdate, db: Session = Depends(get_db)):
    db_operator = crud.update_operator(db, operator_id=operator_id, operator_update=operator_update)
    if db_operator is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return db_operator


# Rental endpoints
@app.post("/rentals/", response_model=schemas.Rental)
def create_rental(rental: schemas.RentalCreate, db: Session = Depends(get_db)):
    # Check if equipment exists and is available
    equipment = crud.get_equipment(db, rental.equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.status != "available":
        raise HTTPException(status_code=400, detail="Equipment is not available for rental")
    
    return crud.create_rental(db=db, rental=rental)


@app.post("/rentals/manual", response_model=schemas.Rental)
def create_rental_manual(rental: schemas.RentalCreate, db: Session = Depends(get_db)):
    """Create rental without equipment availability check - for manual management"""
    # Only check if equipment exists
    equipment = crud.get_equipment(db, rental.equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Create rental without changing equipment status (assume you've already updated it manually)
    return crud.create_rental_manual(db=db, rental=rental)


@app.get("/rentals/", response_model=List[schemas.Rental])
def read_rentals(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    rentals = crud.get_rentals(db, skip=skip, limit=limit, status=status)
    return rentals


@app.get("/rentals/active", response_model=List[schemas.Rental])
def read_active_rentals(db: Session = Depends(get_db)):
    return crud.get_active_rentals(db)


@app.get("/rentals/overdue", response_model=List[schemas.Rental])
def read_overdue_rentals(db: Session = Depends(get_db)):
    return crud.get_overdue_rentals(db)


@app.get("/rentals/{rental_id}", response_model=schemas.Rental)
def read_rental(rental_id: int, db: Session = Depends(get_db)):
    db_rental = crud.get_rental(db, rental_id=rental_id)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return db_rental


@app.put("/rentals/{rental_id}", response_model=schemas.Rental)
def update_rental(rental_id: int, rental_update: schemas.RentalUpdate, db: Session = Depends(get_db)):
    db_rental = crud.update_rental(db, rental_id=rental_id, rental_update=rental_update)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return db_rental


@app.post("/rentals/{rental_id}/checkin", response_model=schemas.Rental)
def check_in_equipment(rental_id: int, db: Session = Depends(get_db)):
    db_rental = crud.check_in_equipment(db, rental_id=rental_id)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return db_rental


# Usage Log endpoints
@app.post("/usage-logs/", response_model=schemas.UsageLog)
def create_usage_log(usage_log: schemas.UsageLogCreate, db: Session = Depends(get_db)):
    return crud.create_usage_log(db=db, usage_log=usage_log)


@app.get("/usage-logs/rental/{rental_id}", response_model=List[schemas.UsageLog])
def read_usage_logs_by_rental(rental_id: int, db: Session = Depends(get_db)):
    return crud.get_usage_logs_by_rental(db, rental_id=rental_id)


@app.get("/usage-logs/equipment/{equipment_id}", response_model=List[schemas.UsageLog])
def read_usage_logs_by_equipment(equipment_id: int, db: Session = Depends(get_db)):
    return crud.get_usage_logs_by_equipment(db, equipment_id=equipment_id)


# Alert endpoints
@app.post("/alerts/", response_model=schemas.Alert)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    return crud.create_alert(db=db, alert=alert)


@app.get("/alerts/", response_model=List[schemas.Alert])
def read_alerts(skip: int = 0, limit: int = 100, is_resolved: Optional[bool] = None, db: Session = Depends(get_db)):
    return crud.get_alerts(db, skip=skip, limit=limit, is_resolved=is_resolved)


@app.put("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, resolved_by: str, db: Session = Depends(get_db)):
    db_alert = crud.resolve_alert(db, alert_id=alert_id, resolved_by=resolved_by)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert resolved successfully"}


# Dashboard and Analytics endpoints
@app.get("/dashboard/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    equipment_summary = crud.get_equipment_summary(db)
    rental_summary = crud.get_rental_summary(db)
    recent_alerts = crud.get_alerts(db, limit=5, is_resolved=False)
    
    return schemas.DashboardSummary(
        equipment_summary=equipment_summary,
        rental_summary=rental_summary,
        recent_alerts=recent_alerts
    )


@app.post("/analytics/detect-anomalies")
def detect_anomalies(db: Session = Depends(get_db)):
    """Run anomaly detection and create alerts"""
    idle_alerts = crud.detect_idle_equipment_anomalies(db)
    overdue_alerts = crud.detect_overdue_rentals(db)
    
    return {
        "message": "Anomaly detection completed",
        "idle_alerts_created": len(idle_alerts),
        "overdue_alerts_created": len(overdue_alerts)
    }





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
