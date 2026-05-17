import logging
from decimal import Decimal
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    BigInteger, String, Boolean, Integer, Numeric, Text,
    ForeignKey, TIMESTAMP, func, UniqueConstraint, Date
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
    tangas: Mapped[int] = mapped_column(Integer, default=50)        # Boshlang'ich 50 tanga
    total_spent: Mapped[int] = mapped_column(Integer, default=0)    # Jami sarflangan tanga
    total_videos: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_video_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_until: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    referral_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    referred_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    last_active: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now(), onupdate=func.now())

    # Relationships
    generations: Mapped[List["VideoGeneration"]] = relationship("VideoGeneration", back_populates="user")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="user")
    subscriptions: Mapped[List["PremiumSubscription"]] = relationship("PremiumSubscription", back_populates="user")


class VideoGeneration(Base):
    __tablename__ = "video_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # pending / processing / done / failed
    api_job_id: Mapped[Optional[str]] = mapped_column(String(200))
    video_url: Mapped[Optional[str]] = mapped_column(Text)
    cost_tangas: Mapped[int] = mapped_column(Integer, default=30)
    duration_sec: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="generations")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    amount_tangas: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(20))
    # stars / manual
    provider_tx_id: Mapped[Optional[str]] = mapped_column(String(200), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # pending / confirmed / cancelled
    package: Mapped[Optional[str]] = mapped_column(String(20))
    # small / medium / large / mega
    admin_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
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


class PremiumSubscription(Base):
    __tablename__ = "premium_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    started_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now())
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    plan: Mapped[str] = mapped_column(String(20))  # monthly/yearly

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscriptions")
