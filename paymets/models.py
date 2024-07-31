from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, ForeignKey, Boolean
from sqlalchemy import Column, TIMESTAMP, DECIMAL, String

from app.db import Base, TimestampsMixin

if TYPE_CHECKING:
    from license_plates.models import Visit

class Price(Base, TimestampsMixin):
    __tablename__ = "prices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hours: Mapped[int] = mapped_column(Integer, unique=True)
    price: Mapped[float] = mapped_column(Float)

class Payment(Base, TimestampsMixin):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    visit_id: Mapped[int] = mapped_column(Integer, ForeignKey('visits.id', ondelete="CASCADE"))
    visit: Mapped["Visit"] = relationship(back_populates='payment')
    total_cost: Mapped[float] = mapped_column(Float)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)

class Parking(Base):
    __tablename__ = 'parkings'

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(20), index=True)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    
class Rate(Base):
    __tablename__ = 'rates'

    id = Column(Integer, primary_key=True, index=True)
    rate_per_hour = Column(DECIMAL, nullable=False)

class Limit(Base):
    __tablename__ = 'limits'

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(20), index=True)
    limit_amount = Column(DECIMAL, nullable=False)