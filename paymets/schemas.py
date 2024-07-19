from typing import List, Optional
from datetime import datetime, UTC
from typing import Optional
from pydantic import Field, BaseModel
from license_plates.schemas import VisitResponse

class Price(BaseModel):
    hours: int
    price: float

class PriceResponse(Price):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Payment(BaseModel):
    total_cost: float
    paid: Optional[bool] = Field(False)

class PaymentResponse(BaseModel):
    id: int
    visit: VisitResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
