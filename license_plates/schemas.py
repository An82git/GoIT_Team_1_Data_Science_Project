from typing import List, Optional
from datetime import datetime, UTC
from typing import Optional
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


class LicensePlateResponse(LicensePlate):
    id: int
    visits: List[VisitResponse]

    class Config:
        from_attributes = True
