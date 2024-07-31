from typing import List, Optional
from datetime import datetime, UTC
from pydantic import Field, BaseModel

class LicensePlate(BaseModel):
    model: str = Field(min_length=5, max_length=255)
    number: str = Field(min_length=3, max_length=10)
    baned: Optional[bool] = Field(False)


class Visit(BaseModel):
    in_at: datetime = Field(datetime.now(UTC))
    out_at: Optional[datetime] = Field(None)

class VisitResponse(Visit):
    id: int

    class Config:
        from_attributes = True

class PaymentVisitResponse(VisitResponse):
    total_cost: float | None

    class Config:
        from_attributes = True

class LicensePlateResponse(LicensePlate):
    id: int
    visits: List[VisitResponse]

    class Config:
        from_attributes = True


class ParkingBase(BaseModel):
    license_plate: str
    start_time: datetime
    end_time: datetime

class ParkingResponse(ParkingBase):
    id: int
    
    class Config:
        from_attributes = True

class RateBase(BaseModel):
    rate_per_hour: float

class RateResponse(RateBase):
    id: int
    
    class Config:
        from_attributes = True

class LimitBase(BaseModel):
    license_plate: str
    limit_amount: float

class LimitResponse(LimitBase):
    id: int
    
    class Config:
        from_attributes = True

class TotalCostResponse(BaseModel):
    license_plate_id: int
    total_cost: float

class ExceededLimitResponse(BaseModel):
    license_plate: str
    total_cost: float
    limit_amount: float