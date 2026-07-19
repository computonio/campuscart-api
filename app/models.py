import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship

from app.database import Base


class RoleEnum(str, enum.Enum):
    buyer = "buyer"
    seller = "seller"
    admin = "admin"


class ListingStatus(str, enum.Enum):
    available = "available"
    sold = "sold"


class RequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    hostel = Column(String, nullable=True)  # e.g. "Malaviya Bhawan" - nice personal touch
    created_at = Column(DateTime, default=datetime.utcnow)

    listings = relationship("Listing", back_populates="seller")
    purchase_requests = relationship("PurchaseRequest", back_populates="buyer")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # textbook, electronics, cycle, other
    price = Column(Float, nullable=False)
    status = Column(Enum(ListingStatus), default=ListingStatus.available)
    created_at = Column(DateTime, default=datetime.utcnow)

    seller = relationship("User", back_populates="listings")
    requests = relationship("PurchaseRequest", back_populates="listing")


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(Enum(RequestStatus), default=RequestStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="requests")
    buyer = relationship("User", back_populates="purchase_requests")
