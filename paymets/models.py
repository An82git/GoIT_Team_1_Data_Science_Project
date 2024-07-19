from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, ForeignKey, Boolean

from app.db import Base, TimestampsMixin

if TYPE_CHECKING:
    from license_plates.models import Visit

class Price(Base, TimestampsMixin):
    __tablename__ = "prices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hours: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)

class Payments(Base, TimestampsMixin):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    visit_id: Mapped[int] = mapped_column(Integer, ForeignKey('visits.id', ondelete="CASCADE"))
    visit: Mapped["Visit"] = relationship(back_populates='payment')
    total_cost: Mapped[float] = mapped_column(Float)
    paid: Mapped[bool] = mapped_column(Boolean, default=False)