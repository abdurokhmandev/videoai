import logging
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    BigInteger, String, Boolean, Integer, Numeric, Text,
    ForeignKey, TIMESTAMP, func, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user_id
    username: Mapped[Optional[str]] = mapped_column(String(100))
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    language: Mapped[str] = mapped_column(String(5), default="uz")
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    total_spent: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    total_videos: Mapped[int] = mapped_column(Integer, default=0)
    free_used: Mapped[bool] = mapped_column(Boolean, default=False)
    referral_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    referred_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    last_active: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now(), onupdate=func.now())

    # Relationships
    generations: Mapped[List["VideoGeneration"]] = relationship("VideoGeneration", back_populates="user")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="user")


class VideoGeneration(Base):
    __tablename__ = "video_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_uz: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # pending / processing / done / failed
    api_provider: Mapped[Optional[str]] = mapped_column(String(50))
    # siliconflow / atlascloud
    api_job_id: Mapped[Optional[str]] = mapped_column(String(200))
    video_url: Mapped[Optional[str]] = mapped_column(Text)
    cost_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4))
    cost_som: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    duration_sec: Mapped[int] = mapped_column(Integer, default=8)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="generations")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(20))
    # payme / click
    provider_tx_id: Mapped[Optional[str]] = mapped_column(String(200), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # pending / confirmed / cancelled
    package: Mapped[Optional[str]] = mapped_column(String(20))
    # starter / standard / pro / enterprise
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="payments")


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    referred_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    bonus_given: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())

    __table_args__ = (
        UniqueConstraint("referrer_id", "referred_id", name="uq_referral_pair"),
    )
