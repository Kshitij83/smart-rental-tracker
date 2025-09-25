from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional
from app import models
from app import schemas


# Equipment CRUD
def get_equipment(db: Session, equipment_id: int):
    return db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()


def get_equipment_by_equipment_id(db: Session, equipment_id: str):
    return db.query(models.Equipment).filter(models.Equipment.equipment_id == equipment_id).first()


def get_equipment_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Equipment).offset(skip).limit(limit).all()


def create_equipment(db: Session, equipment: schemas.EquipmentCreate):
    db_equipment = models.Equipment(**equipment.dict())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


def update_equipment(db: Session, equipment_id: int, equipment_update: schemas.EquipmentUpdate):
    db_equipment = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()
    if db_equipment:
        update_data = equipment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_equipment, field, value)
        db_equipment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_equipment)
    return db_equipment


# Site CRUD
def get_site(db: Session, site_id: int):
    return db.query(models.Site).filter(models.Site.id == site_id).first()


def get_site_by_site_id(db: Session, site_id: str):
    return db.query(models.Site).filter(models.Site.site_id == site_id).first()


def get_sites(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Site).offset(skip).limit(limit).all()


def create_site(db: Session, site: schemas.SiteCreate):
    db_site = models.Site(**site.dict())
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site


# Operator CRUD
def get_operator(db: Session, operator_id: int):
    return db.query(models.Operator).filter(models.Operator.id == operator_id).first()


def get_operator_by_operator_id(db: Session, operator_id: str):
    return db.query(models.Operator).filter(models.Operator.operator_id == operator_id).first()


def get_operators(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Operator).offset(skip).limit(limit).all()


def create_operator(db: Session, operator: schemas.OperatorCreate):
    db_operator = models.Operator(**operator.dict())
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator


def update_operator(db: Session, operator_id: int, operator_update: schemas.OperatorUpdate):
    db_operator = db.query(models.Operator).filter(models.Operator.id == operator_id).first()
    if db_operator is None:
        return None
    
    # Update only the fields that are provided
    update_data = operator_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_operator, key, value)
    
    db.commit()
    db.refresh(db_operator)
    return db_operator


# Rental CRUD
def get_rental(db: Session, rental_id: int):
    return db.query(models.Rental).filter(models.Rental.id == rental_id).first()


def get_rentals(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None):
    query = db.query(models.Rental)
    if status:
        query = query.filter(models.Rental.status == status)
    return query.offset(skip).limit(limit).all()


def get_active_rentals(db: Session):
    return db.query(models.Rental).filter(models.Rental.status == "active").all()


def get_overdue_rentals(db: Session):
    current_time = datetime.utcnow()
    return db.query(models.Rental).filter(
        and_(
            models.Rental.status == "active",
            models.Rental.expected_return_date < current_time
        )
    ).all()


def create_rental(db: Session, rental: schemas.RentalCreate):
    db_rental = models.Rental(**rental.dict(), status="active")
    
    # Update equipment status to rented
    equipment = db.query(models.Equipment).filter(models.Equipment.id == rental.equipment_id).first()
    if equipment:
        equipment.status = "rented"
    
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental


def create_rental_manual(db: Session, rental: schemas.RentalCreate):
    """Create rental without changing equipment status - for manual management"""
    db_rental = models.Rental(**rental.dict(), status="active")
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental


def update_rental(db: Session, rental_id: int, rental_update: schemas.RentalUpdate):
    db_rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if db_rental:
        update_data = rental_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rental, field, value)
        db_rental.updated_at = datetime.utcnow()
        
        # If checking in equipment, update equipment status
        if rental_update.check_in_date and rental_update.status == "completed":
            equipment = db.query(models.Equipment).filter(models.Equipment.id == db_rental.equipment_id).first()
            if equipment:
                equipment.status = "available"
        
        db.commit()
        db.refresh(db_rental)
    return db_rental


def check_in_equipment(db: Session, rental_id: int):
    db_rental = db.query(models.Rental).filter(models.Rental.id == rental_id).first()
    if db_rental and db_rental.status == "active":
        db_rental.check_in_date = datetime.utcnow()
        db_rental.status = "completed"
        
        # Calculate total cost if rental rate is available
        if db_rental.rental_rate_per_day:
            rental_days = (db_rental.check_in_date - db_rental.check_out_date).days + 1
            db_rental.total_cost = rental_days * db_rental.rental_rate_per_day
        
        # Update equipment status
        equipment = db.query(models.Equipment).filter(models.Equipment.id == db_rental.equipment_id).first()
        if equipment:
            equipment.status = "available"
        
        db.commit()
        db.refresh(db_rental)
    return db_rental


# Usage Log CRUD
def create_usage_log(db: Session, usage_log: schemas.UsageLogCreate):
    db_usage_log = models.UsageLog(**usage_log.dict())
    db.add(db_usage_log)
    db.commit()
    db.refresh(db_usage_log)
    return db_usage_log


def get_usage_logs_by_rental(db: Session, rental_id: int):
    return db.query(models.UsageLog).filter(models.UsageLog.rental_id == rental_id).all()


def get_usage_logs_by_equipment(db: Session, equipment_id: int):
    return db.query(models.UsageLog).filter(models.UsageLog.equipment_id == equipment_id).all()


# Alert CRUD
def create_alert(db: Session, alert: schemas.AlertCreate):
    db_alert = models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


def get_alerts(db: Session, skip: int = 0, limit: int = 100, is_resolved: Optional[bool] = None):
    query = db.query(models.Alert)
    if is_resolved is not None:
        query = query.filter(models.Alert.is_resolved == is_resolved)
    return query.order_by(models.Alert.created_at.desc()).offset(skip).limit(limit).all()


def resolve_alert(db: Session, alert_id: int, resolved_by: str):
    db_alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if db_alert:
        db_alert.is_resolved = True
        db_alert.resolved_at = datetime.utcnow()
        db_alert.resolved_by = resolved_by
        db.commit()
        db.refresh(db_alert)
    return db_alert


# Dashboard Analytics
def get_equipment_summary(db: Session):
    total = db.query(models.Equipment).count()
    available = db.query(models.Equipment).filter(models.Equipment.status == "available").count()
    rented = db.query(models.Equipment).filter(models.Equipment.status == "rented").count()
    maintenance = db.query(models.Equipment).filter(models.Equipment.status == "maintenance").count()
    
    overdue_count = db.query(models.Rental).filter(
        and_(
            models.Rental.status == "active",
            models.Rental.expected_return_date < datetime.utcnow()
        )
    ).count()
    
    return schemas.EquipmentSummary(
        total_equipment=total,
        available=available,
        rented=rented,
        maintenance=maintenance,
        overdue_rentals=overdue_count
    )


def get_rental_summary(db: Session):
    active_rentals = db.query(models.Rental).filter(models.Rental.status == "active").count()
    overdue_rentals = db.query(models.Rental).filter(
        and_(
            models.Rental.status == "active",
            models.Rental.expected_return_date < datetime.utcnow()
        )
    ).count()
    
    # Calculate total revenue from completed rentals
    total_revenue = db.query(func.sum(models.Rental.total_cost)).filter(
        models.Rental.status == "completed"
    ).scalar() or 0.0
    
    # Calculate equipment utilization
    total_equipment = db.query(models.Equipment).count()
    rented_equipment = db.query(models.Equipment).filter(models.Equipment.status == "rented").count()
    utilization = (rented_equipment / total_equipment * 100) if total_equipment > 0 else 0
    
    return schemas.RentalSummary(
        active_rentals=active_rentals,
        overdue_rentals=overdue_rentals,
        total_revenue=total_revenue,
        equipment_utilization=utilization
    )


def get_equipment_with_status(db: Session, skip: int = 0, limit: int = 100):
    equipment_list = db.query(models.Equipment).offset(skip).limit(limit).all()
    result = []
    
    for equipment in equipment_list:
        # Get current active rental
        current_rental = db.query(models.Rental).filter(
            and_(
                models.Rental.equipment_id == equipment.id,
                models.Rental.status == "active"
            )
        ).first()
        
        # Calculate total runtime hours
        total_hours = db.query(func.sum(models.UsageLog.engine_hours)).filter(
            models.UsageLog.equipment_id == equipment.id
        ).scalar() or 0.0
        
        equipment_data = schemas.EquipmentWithStatus(
            **equipment.__dict__,
            current_rental=current_rental,
            total_runtime_hours=total_hours,
            utilization_rate=0.0  # This would need more complex calculation
        )
        result.append(equipment_data)
    
    return result


# Anomaly Detection Helpers
def detect_idle_equipment_anomalies(db: Session, idle_threshold_hours: float = 10.0):
    """Detect equipment with excessive idle hours"""
    recent_date = datetime.utcnow() - timedelta(days=7)
    
    idle_equipment = db.query(models.UsageLog).filter(
        and_(
            models.UsageLog.date >= recent_date,
            models.UsageLog.idle_hours > idle_threshold_hours
        )
    ).all()
    
    alerts = []
    for log in idle_equipment:
        alert = schemas.AlertCreate(
            equipment_id=log.equipment_id,
            rental_id=log.rental_id,
            alert_type="anomaly",
            severity="medium",
            title="Excessive Idle Time Detected",
            description=f"Equipment has {log.idle_hours} idle hours on {log.date.date()}"
        )
        alerts.append(create_alert(db, alert))
    
    return alerts


def detect_overdue_rentals(db: Session):
    """Create alerts for overdue rentals"""
    overdue_rentals = get_overdue_rentals(db)
    alerts = []
    
    for rental in overdue_rentals:
        # Check if alert already exists for this rental
        existing_alert = db.query(models.Alert).filter(
            and_(
                models.Alert.rental_id == rental.id,
                models.Alert.alert_type == "overdue",
                models.Alert.is_resolved == False
            )
        ).first()
        
        if not existing_alert:
            days_overdue = (datetime.utcnow() - rental.expected_return_date).days
            alert = schemas.AlertCreate(
                rental_id=rental.id,
                equipment_id=rental.equipment_id,
                alert_type="overdue",
                severity="high" if days_overdue > 7 else "medium",
                title="Rental Overdue",
                description=f"Equipment rental is {days_overdue} days overdue"
            )
            alerts.append(create_alert(db, alert))
    
    return alerts


# Demand Forecast CRUD
def create_demand_forecast(db: Session, forecast_data: dict):
    """Create a new demand forecast record"""
    db_forecast = models.DemandForecast(**forecast_data)
    db.add(db_forecast)
    db.commit()
    db.refresh(db_forecast)
    return db_forecast


def get_demand_forecasts(
    db: Session, 
    site_id: Optional[str] = None, 
    equipment_type: Optional[str] = None,
    days_back: int = 30
):
    """Get demand forecasts with optional filtering"""
    query = db.query(models.DemandForecast)
    
    if site_id:
        query = query.filter(models.DemandForecast.site_id == site_id)
    
    if equipment_type:
        query = query.filter(models.DemandForecast.equipment_type == equipment_type)
    
    if days_back:
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = query.filter(models.DemandForecast.forecast_date >= cutoff_date)
    
    return query.order_by(models.DemandForecast.forecast_date.desc()).all()


def update_demand_forecast_actual(db: Session, forecast_id: int, actual_demand: int):
    """Update forecast with actual demand for model validation"""
    db_forecast = db.query(models.DemandForecast).filter(
        models.DemandForecast.id == forecast_id
    ).first()
    
    if db_forecast:
        db_forecast.actual_demand = actual_demand
        db.commit()
        db.refresh(db_forecast)
    
    return db_forecast