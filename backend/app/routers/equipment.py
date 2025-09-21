from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas
from .. import crud
from .. import models
from ..database import get_db
from datetime import datetime
from sqlalchemy import and_

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.post("/", response_model=schemas.Equipment)
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    db_equipment = crud.get_equipment_by_equipment_id(db, equipment_id=equipment.equipment_id)
    if db_equipment:
        raise HTTPException(status_code=400, detail="Equipment ID already registered")
    return crud.create_equipment(db=db, equipment=equipment)


@router.get("/", response_model=List[schemas.Equipment])
def read_equipment(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    equipment = crud.get_equipment_list(db, skip=skip, limit=limit)
    return equipment


@router.get("/status/detailed", response_model=List[schemas.EquipmentWithStatus])
def read_equipment_with_status(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    return crud.get_equipment_with_status(db, skip=skip, limit=limit)


@router.get("/{equipment_id}", response_model=schemas.Equipment)
def read_equipment_by_id(equipment_id: int, db: Session = Depends(get_db)):
    db_equipment = crud.get_equipment(db, equipment_id=equipment_id)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return db_equipment


@router.put("/{equipment_id}", response_model=schemas.Equipment)
def update_equipment(equipment_id: int, equipment_update: schemas.EquipmentUpdate, db: Session = Depends(get_db)):
    db_equipment = crud.update_equipment(db, equipment_id=equipment_id, equipment_update=equipment_update)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return db_equipment


@router.get("/all")
def read_all_equipment(db: Session = Depends(get_db)):
    """Get all equipment from database without pagination limits"""
    equipment = crud.get_equipment_list(db, skip=0, limit=10000)  # Very high limit to get all
    return equipment


@router.get("/count")
def get_equipment_count(db: Session = Depends(get_db)):
    """Get total count of equipment in database"""
    count = db.query(models.Equipment).count()
    return {"total_equipment": count}


@router.post("/{equipment_id}/return")
def return_equipment(equipment_id: str, db: Session = Depends(get_db)):
    """Return equipment and make it available for rent"""
    # Find equipment by equipment_id (string identifier)
    db_equipment = crud.get_equipment_by_equipment_id(db, equipment_id=equipment_id)
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Update equipment status to available
    db_equipment.status = "available"
    db_equipment.site_id = None  # Remove site assignment
    db_equipment.updated_at = datetime.utcnow()
    
    # If there's an active rental, mark it as completed
    active_rental = db.query(models.Rental).filter(
        and_(
            models.Rental.equipment_id == db_equipment.id,
            models.Rental.status == "active"
        )
    ).first()
    
    if active_rental:
        active_rental.status = "completed"
        active_rental.check_in_date = datetime.utcnow()
    
    db.commit()
    db.refresh(db_equipment)
    
    return {
        "message": f"Equipment {equipment_id} has been returned and is now available",
        "equipment_id": equipment_id,
        "status": "available"
    }


@router.put("/{equipment_id}/status")
def update_equipment_status(equipment_id: str, status_update: dict, db: Session = Depends(get_db)):
    """Update equipment status and related fields"""
    db_equipment = crud.get_equipment_by_equipment_id(db, equipment_id=equipment_id)
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Update status
    if "status" in status_update:
        db_equipment.status = status_update["status"]
    
    # Update site_id if provided
    if "site_id" in status_update:
        db_equipment.site_id = status_update["site_id"]
    
    # Update other fields if provided
    for field in ["type", "engine_hours_per_day", "idle_hours_per_day"]:
        if field in status_update:
            setattr(db_equipment, field, status_update[field])
    
    db_equipment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_equipment)
    
    return db_equipment


@router.get("/paginated")
def read_equipment_paginated(
    page: int = 1, 
    limit: int = 10, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get equipment with pagination and optional status filter"""
    skip = (page - 1) * limit
    
    # Build query
    query = db.query(models.Equipment)
    if status:
        query = query.filter(models.Equipment.status == status)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    equipment = query.offset(skip).limit(limit).all()
    
    return {
        "items": equipment,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }
