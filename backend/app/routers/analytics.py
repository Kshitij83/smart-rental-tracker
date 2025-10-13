from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas
from .. import crud
from ..database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    equipment_summary = crud.get_equipment_summary(db)
    rental_summary = crud.get_rental_summary(db)
    recent_alerts = crud.get_alerts(db, limit=5, is_resolved=False)
    
    return schemas.DashboardSummary(
        equipment_summary=equipment_summary,
        rental_summary=rental_summary,
        recent_alerts=recent_alerts
    )


@router.post("/detect-anomalies")
def detect_anomalies(db: Session = Depends(get_db)):
    """Run anomaly detection and create alerts"""
    idle_alerts = crud.detect_idle_equipment_anomalies(db)
    overdue_alerts = crud.detect_overdue_rentals(db)
    
    return {
        "message": "Anomaly detection completed",
        "idle_alerts_created": len(idle_alerts),
        "overdue_alerts_created": len(overdue_alerts)
    }


@router.get("/usage-logs/rental/{rental_id}", response_model=List[schemas.UsageLog])
def read_usage_logs_by_rental(rental_id: int, db: Session = Depends(get_db)):
    return crud.get_usage_logs_by_rental(db, rental_id=rental_id)


@router.get("/usage-logs/equipment/{equipment_id}", response_model=List[schemas.UsageLog])
def read_usage_logs_by_equipment(equipment_id: int, db: Session = Depends(get_db)):
    return crud.get_usage_logs_by_equipment(db, equipment_id=equipment_id)


@router.post("/usage-logs/", response_model=schemas.UsageLog)
def create_usage_log(usage_log: schemas.UsageLogCreate, db: Session = Depends(get_db)):
    return crud.create_usage_log(db=db, usage_log=usage_log)


@router.get("/alerts/", response_model=List[schemas.Alert])
def read_alerts(skip: int = 0, limit: int = 100, is_resolved: Optional[bool] = None, db: Session = Depends(get_db)):
    return crud.get_alerts(db, skip=skip, limit=limit, is_resolved=is_resolved)


@router.post("/alerts/", response_model=schemas.Alert)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    return crud.create_alert(db=db, alert=alert)


@router.put("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, resolved_by: str, db: Session = Depends(get_db)):
    db_alert = crud.resolve_alert(db, alert_id=alert_id, resolved_by=resolved_by)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert resolved successfully"}
