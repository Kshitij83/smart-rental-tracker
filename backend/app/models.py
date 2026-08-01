from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String, unique=True, index=True, nullable=False)  # EQX1001, etc.
    type = Column(String, nullable=False)  # Excavator, Crane, Bulldozer, etc.
    site_id = Column(String, nullable=True)  # S001, S002, etc. (changed from user_id)
    check_out_date = Column(String, nullable=True)  # Date string from CSV
    check_in_date = Column(String, nullable=True)   # Date string from CSV
    engine_hours_per_day = Column(Float, default=0.0)
    idle_hours_per_day = Column(Float, default=0.0)
    operating_days = Column(Integer, default=0)
    last_operator_id = Column(String, nullable=True)  # OP401, OP402, etc.
    
    # Additional fields for equipment management
    model = Column(String)
    manufacturer = Column(String)
    year = Column(Integer)
    serial_number = Column(String)
    status = Column(String, default="available")  # available, rented, maintenance, retired
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rentals = relationship("Rental", back_populates="equipment")
    usage_logs = relationship("UsageLog", back_populates="equipment")


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String, unique=True, index=True, nullable=False)  # S001, S002, etc.
    name = Column(String, nullable=False)
    location = Column(String)
    address = Column(Text)
    contact_person = Column(String)
    contact_phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rentals = relationship("Rental", back_populates="site")


class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(String, unique=True, index=True, nullable=False)  # OP101, OP103, etc.
    name = Column(String, nullable=False)
    license_number = Column(String)
    phone = Column(String)
    email = Column(String)
    certification_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rentals = relationship("Rental", back_populates="operator")
    usage_logs = relationship("UsageLog", back_populates="operator")


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    
    check_out_date = Column(DateTime, nullable=False)
    check_in_date = Column(DateTime, nullable=True)
    expected_return_date = Column(DateTime)
    
    rental_rate_per_day = Column(Float)
    total_cost = Column(Float)
    
    status = Column(String, default="active")  # active, completed, overdue, cancelled
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="rentals")
    site = relationship("Site", back_populates="rentals")
    operator = relationship("Operator", back_populates="rentals")
    usage_logs = relationship("UsageLog", back_populates="rental")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    
    date = Column(DateTime, nullable=False)
    engine_hours = Column(Float, default=0.0)
    idle_hours = Column(Float, default=0.0)
    fuel_usage = Column(Float, default=0.0)  # in liters or gallons
    location_lat = Column(Float)
    location_lng = Column(Float)
    
    # Maintenance and condition tracking
    condition_rating = Column(Integer)  # 1-10 scale
    maintenance_required = Column(Boolean, default=False)
    maintenance_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rental = relationship("Rental", back_populates="usage_logs")
    equipment = relationship("Equipment", back_populates="usage_logs")
    operator = relationship("Operator", back_populates="usage_logs")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=True)
    
    alert_type = Column(String, nullable=False)  # overdue, maintenance, anomaly, etc.
    severity = Column(String, default="medium")  # low, medium, high, critical
    title = Column(String, nullable=False)
    description = Column(Text)
    
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    
    maintenance_type = Column(String, nullable=False)  # routine, repair, inspection
    description = Column(Text)
    cost = Column(Float)
    
    scheduled_date = Column(DateTime)
    completed_date = Column(DateTime)
    next_maintenance_date = Column(DateTime)
    
    technician_name = Column(String)
    vendor = Column(String)
    
    status = Column(String, default="scheduled")  # scheduled, in_progress, completed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    equipment_type = Column(String, nullable=False)
    
    forecast_date = Column(DateTime, nullable=False)
    predicted_demand = Column(Integer, nullable=False)
    confidence_score = Column(Float)  # 0.0 to 1.0
    
    actual_demand = Column(Integer)  # filled in later for model validation
    
    created_at = Column(DateTime, default=datetime.utcnow)
