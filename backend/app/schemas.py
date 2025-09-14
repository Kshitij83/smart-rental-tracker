# Smart Rental Tracking System - Backend App Package

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# Equipment Schemas
class EquipmentBase(BaseModel):
    equipment_id: str
    type: str
    site_id: Optional[str] = None
    check_out_date: Optional[str] = None
    check_in_date: Optional[str] = None
    engine_hours_per_day: Optional[float] = 0.0
    idle_hours_per_day: Optional[float] = 0.0
    operating_days: Optional[int] = 0
    last_operator_id: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    year: Optional[int] = None
    serial_number: Optional[str] = None
    status: str = "available"


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    type: Optional[str] = None
    site_id: Optional[str] = None
    check_out_date: Optional[str] = None
    check_in_date: Optional[str] = None
    engine_hours_per_day: Optional[float] = None
    idle_hours_per_day: Optional[float] = None
    operating_days: Optional[int] = None
    last_operator_id: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    year: Optional[int] = None
    serial_number: Optional[str] = None
    status: Optional[str] = None


class Equipment(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Site Schemas
class SiteBase(BaseModel):
    site_id: str
    name: str
    location: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None


class SiteCreate(SiteBase):
    pass


class Site(SiteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Operator Schemas
class OperatorBase(BaseModel):
    operator_id: str
    name: str
    license_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    certification_level: Optional[str] = None


class OperatorCreate(OperatorBase):
    pass


class OperatorUpdate(BaseModel):
    name: Optional[str] = None
    license_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    certification_level: Optional[str] = None


class Operator(OperatorBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Rental Schemas
class RentalBase(BaseModel):
    equipment_id: int
    site_id: Optional[int] = None
    operator_id: Optional[int] = None
    check_out_date: datetime
    expected_return_date: Optional[datetime] = None
    rental_rate_per_day: Optional[float] = None


class RentalCreate(RentalBase):
    pass


class RentalUpdate(BaseModel):
    site_id: Optional[int] = None
    operator_id: Optional[int] = None
    check_in_date: Optional[datetime] = None
    expected_return_date: Optional[datetime] = None
    rental_rate_per_day: Optional[float] = None
    total_cost: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Rental(RentalBase):
    id: int
    check_in_date: Optional[datetime] = None
    total_cost: Optional[float] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related objects
    equipment: Equipment
    site: Optional[Site] = None
    operator: Optional[Operator] = None

    class Config:
        from_attributes = True


# Usage Log Schemas
class UsageLogBase(BaseModel):
    rental_id: int
    equipment_id: int
    operator_id: Optional[int] = None
    date: datetime
    engine_hours: float = 0.0
    idle_hours: float = 0.0
    fuel_usage: float = 0.0
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    condition_rating: Optional[int] = None
    maintenance_required: bool = False
    maintenance_notes: Optional[str] = None


class UsageLogCreate(UsageLogBase):
    pass


class UsageLog(UsageLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Alert Schemas
class AlertBase(BaseModel):
    rental_id: Optional[int] = None
    equipment_id: Optional[int] = None
    alert_type: str
    severity: str
    title: str
    description: str
    resolved: bool = False


class AlertCreate(AlertBase):
    pass


class Alert(AlertBase):
    id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Demand Forecast Schemas
class DemandForecastBase(BaseModel):
    site_id: str
    equipment_type: str
    forecast_date: datetime
    predicted_demand: int
    confidence_score: float
    actual_demand: Optional[int] = None


class DemandForecastCreate(DemandForecastBase):
    pass


class DemandForecast(DemandForecastBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Equipment with Status Schema (for detailed views)
class EquipmentWithStatus(BaseModel):
    id: int
    equipment_id: str
    type: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    year: Optional[int] = None
    serial_number: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Current rental info
    current_rental: Optional[Rental] = None
    current_site: Optional[Site] = None
    current_operator: Optional[Operator] = None

    class Config:
        from_attributes = True


# Rental with Details Schema
class RentalWithDetails(BaseModel):
    id: int
    equipment_id: int
    site_id: Optional[int] = None
    operator_id: Optional[int] = None
    check_out_date: datetime
    check_in_date: Optional[datetime] = None
    expected_return_date: Optional[datetime] = None
    rental_rate_per_day: Optional[float] = None
    total_cost: Optional[float] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Related objects
    equipment: Equipment
    site: Optional[Site] = None
    operator: Optional[Operator] = None

    class Config:
        from_attributes = True


# Dashboard Summary Schemas
class EquipmentSummary(BaseModel):
    total_equipment: int
    available: int
    rented: int
    maintenance: int
    overdue_rentals: int


class RentalSummary(BaseModel):
    active_rentals: int
    overdue_rentals: int
    total_revenue: float
    equipment_utilization: float


class DashboardSummary(BaseModel):
    equipment_summary: EquipmentSummary
    rental_summary: RentalSummary
    recent_alerts: List[Alert]
