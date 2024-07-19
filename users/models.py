from enum import Enum
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Enum as SQLEnum, DateTime, Column

from app.db import Base, TimestampsMixin

if TYPE_CHECKING:
    from license_plates.models import LicensePlate


class UserRoles(Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base, TimestampsMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(200))
    role = Column(SQLEnum(UserRoles), default=UserRoles.USER)
    tokens: Mapped[List["Token"]] = relationship(back_populates="user")
    license_plates: Mapped[List["LicensePlate"]] = relationship(back_populates="user")


class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String, unique=True)
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="tokens")

    