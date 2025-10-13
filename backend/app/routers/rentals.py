from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from .. import schemas
from .. import crud
from ..database import get_db
from ..notification_service import NotificationService
from .. import models

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.post("/", response_model=schemas.Rental)
def create_rental(rental: schemas.RentalCreate, db: Session = Depends(get_db)):
    # Check if equipment exists and is available
    equipment = crud.get_equipment(db, rental.equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.status != "available":
        raise HTTPException(status_code=400, detail="Equipment is not available for rental")
    
    # Create the rental (this starts the timer automatically)
    db_rental = crud.create_rental(db=db, rental=rental)
    
    # Send confirmation email to site contact
    if db_rental.site_id:
        notification_service = NotificationService()
        site = crud.get_site(db, db_rental.site_id)
        if site and site.contact_person:
            notification_service.send_rental_confirmation(db_rental.id)
    
    return db_rental


@router.get("/", response_model=List[schemas.Rental])
def read_rentals(skip: int = 0, limit: int = 1000, status: Optional[str] = None, db: Session = Depends(get_db)):
    rentals = crud.get_rentals(db, skip=skip, limit=limit, status=status)
    return rentals


@router.get("/active", response_model=List[schemas.Rental])
def read_active_rentals(db: Session = Depends(get_db)):
    return crud.get_active_rentals(db)


@router.get("/overdue", response_model=List[schemas.Rental])
def read_overdue_rentals(db: Session = Depends(get_db)):
    return crud.get_overdue_rentals(db)


@router.get("/due-soon", response_model=List[schemas.Rental])
def read_rentals_due_soon(days_ahead: int = 7, db: Session = Depends(get_db)):
    """Get rentals that are due within the specified number of days"""
    return crud.get_rentals_due_soon(db, days_ahead)


@router.get("/all")
def read_all_rentals(db: Session = Depends(get_db)):
    """Get all rentals from database without pagination limits"""
    rentals = crud.get_rentals(db, skip=0, limit=10000, status=None)
    return rentals


@router.get("/paginated")
def read_rentals_paginated(
    page: int = 1, 
    limit: int = 10, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get rentals with pagination and optional status filter"""
    skip = (page - 1) * limit
    
    # Build query
    query = db.query(models.Rental)
    if status:
        query = query.filter(models.Rental.status == status)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    rentals = query.offset(skip).limit(limit).all()
    
    return {
        "items": rentals,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/{rental_id}", response_model=schemas.Rental)
def read_rental(rental_id: int, db: Session = Depends(get_db)):
    db_rental = crud.get_rental(db, rental_id=rental_id)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return db_rental


@router.put("/{rental_id}", response_model=schemas.Rental)
def update_rental(rental_id: int, rental_update: schemas.RentalUpdate, db: Session = Depends(get_db)):
    db_rental = crud.update_rental(db, rental_id=rental_id, rental_update=rental_update)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return db_rental


@router.post("/{rental_id}/checkin", response_model=schemas.Rental)
def check_in_equipment(rental_id: int, db: Session = Depends(get_db)):
    db_rental = crud.check_in_equipment(db, rental_id=rental_id)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Send return confirmation email
    notification_service = NotificationService()
    notification_service.send_return_confirmation(rental_id)
    
    return db_rental


@router.post("/{rental_id}/extend", response_model=schemas.Rental)
def extend_rental(rental_id: int, extension_days: int, db: Session = Depends(get_db)):
    """Extend a rental by the specified number of days"""
    db_rental = crud.extend_rental(db, rental_id=rental_id, extension_days=extension_days)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    # Send extension confirmation email
    notification_service = NotificationService()
    notification_service.send_extension_confirmation(rental_id, extension_days)
    
    return db_rental


@router.get("/{rental_id}/timer", response_model=Dict)
def get_rental_timer(rental_id: int, db: Session = Depends(get_db)):
    """Get real-time rental timer information"""
    db_rental = crud.get_rental(db, rental_id=rental_id)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    if db_rental.status != "active":
        return {
            "rental_id": rental_id,
            "status": db_rental.status,
            "message": "Rental is not active"
        }
    
    # Calculate timer information
    current_time = datetime.utcnow()
    rental_start = db_rental.check_out_date
    expected_return = db_rental.expected_return_date
    
    # Calculate elapsed time
    elapsed_days = (current_time - rental_start).days
    elapsed_hours = (current_time - rental_start).total_seconds() / 3600
    
    # Calculate time remaining
    if expected_return:
        time_remaining = expected_return - current_time
        days_remaining = time_remaining.days
        hours_remaining = time_remaining.total_seconds() / 3600
        
        # Check if overdue
        is_overdue = time_remaining.total_seconds() < 0
        overdue_days = abs(days_remaining) if is_overdue else 0
    else:
        days_remaining = None
        hours_remaining = None
        is_overdue = False
        overdue_days = 0
    
    return {
        "rental_id": rental_id,
        "equipment_id": db_rental.equipment.equipment_id,
        "equipment_type": db_rental.equipment.type,
        "rental_start": rental_start.isoformat(),
        "expected_return": expected_return.isoformat() if expected_return else None,
        "elapsed_days": elapsed_days,
        "elapsed_hours": round(elapsed_hours, 2),
        "days_remaining": days_remaining,
        "hours_remaining": round(hours_remaining, 2) if hours_remaining else None,
        "is_overdue": is_overdue,
        "overdue_days": overdue_days,
        "status": "overdue" if is_overdue else "active",
        "current_time": current_time.isoformat()
    }


@router.post("/{rental_id}/usage-log", response_model=schemas.UsageLog)
def log_equipment_usage(rental_id: int, usage_data: schemas.UsageLogCreate, db: Session = Depends(get_db)):
    """Log equipment usage data (engine hours, fuel, location, etc.)"""
    # Verify rental exists and is active
    db_rental = crud.get_rental(db, rental_id=rental_id)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    if db_rental.status != "active":
        raise HTTPException(status_code=400, detail="Cannot log usage for inactive rental")
    
    # Create usage log
    usage_log = crud.create_usage_log(db, usage_data)
    
    # Check for anomalies using ML system
    try:
        from ..ml_integration import check_usage_anomalies
        anomalies = check_usage_anomalies(rental_id, usage_data)
        if anomalies:
            # Create alert for anomalies
            alert = models.Alert(
                rental_id=rental_id,
                equipment_id=db_rental.equipment_id,
                alert_type="usage_anomaly",
                severity="medium",
                title=f"Usage anomaly detected for {db_rental.equipment.equipment_id}",
                description=f"Anomaly detected: {anomalies}"
            )
            db.add(alert)
            db.commit()
    except Exception as e:
        # ML system not available, continue without anomaly detection
        pass
    
    return usage_log


@router.get("/{rental_id}/usage-logs", response_model=List[schemas.UsageLog])
def get_rental_usage_logs(rental_id: int, db: Session = Depends(get_db)):
    """Get all usage logs for a specific rental"""
    db_rental = crud.get_rental(db, rental_id=rental_id)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    return crud.get_usage_logs_by_rental(db, rental_id)


@router.post("/{rental_id}/send-reminder", response_model=Dict)
def send_manual_reminder(rental_id: int, db: Session = Depends(get_db)):
    """Manually send a return reminder for a specific rental"""
    db_rental = crud.get_rental(db, rental_id=rental_id)
    if db_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    if db_rental.status != "active":
        raise HTTPException(status_code=400, detail="Cannot send reminder for inactive rental")
    
    notification_service = NotificationService()
    result = notification_service.send_single_reminder(rental_id)
    
    return {
        "rental_id": rental_id,
        "reminder_sent": result.get("success", False),
        "message": result.get("message", "Reminder sent successfully")
    }


@router.post("/send-all-reminders", response_model=Dict)
def send_all_reminders(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Send reminders for all rentals due soon (background task)"""
    notification_service = NotificationService()
    
    # Run in background to avoid blocking the API
    background_tasks.add_task(notification_service.send_return_reminders)
    
    return {
        "message": "Reminder process started in background",
        "status": "processing"
    }


@router.post("/send-overdue-alerts", response_model=Dict)
def send_overdue_alerts(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Send overdue alerts for all overdue rentals (background task)"""
    notification_service = NotificationService()
    
    # Run in background to avoid blocking the API
    background_tasks.add_task(notification_service.send_overdue_notifications)
    
    return {
        "message": "Overdue alert process started in background",
        "status": "processing"
    }


@router.get("/analytics/summary", response_model=Dict)
def get_rental_analytics_summary(db: Session = Depends(get_db)):
    """Get rental analytics summary"""
    return crud.get_rental_analytics_summary(db)


@router.get("/analytics/equipment/{equipment_id}", response_model=Dict)
def get_equipment_rental_history(equipment_id: int, db: Session = Depends(get_db)):
    """Get rental history for a specific equipment"""
    equipment = crud.get_equipment(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    return crud.get_equipment_rental_history(db, equipment_id)


@router.get("/analytics/site/{site_id}", response_model=Dict)
def get_site_rental_analytics(site_id: int, db: Session = Depends(get_db)):
    """Get rental analytics for a specific site"""
    site = crud.get_site(db, site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    return crud.get_site_rental_analytics(db, site_id)
