from datetime import datetime, UTC
from typing import TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean

from app.db import Base, TimestampsMixin

if TYPE_CHECKING:
    from users.models import User
    from paymets.models import Payment

class LicensePlate(Base, TimestampsMixin):
    __tablename__ = "license_plates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="license_plates")
    visits: Mapped[List["Visit"]] = relationship(back_populates="license_plate")
    number: Mapped[int] = mapped_column(String(7), unique=True)
    baned: Mapped[bool] = mapped_column(Boolean, default=False)

class Visit(Base):
    __tablename__ = "visits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    license_plate_id: Mapped[int] = mapped_column(Integer, ForeignKey("license_plates.id", ondelete="CASCADE"))
    license_plate: Mapped[LicensePlate] = relationship(back_populates="visits")
    payment: Mapped["Payment"] = relationship(back_populates='visit')
    in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    out_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))