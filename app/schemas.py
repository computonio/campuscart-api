from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import RoleEnum, ListingStatus, RequestStatus


# ---------- Users ----------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleEnum
    hostel: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: RoleEnum
    hostel: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Listings ----------
class ListingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    price: float


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    status: Optional[ListingStatus] = None


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    seller_id: int
    title: str
    description: Optional[str] = None
    category: str
    price: float
    status: ListingStatus
    created_at: datetime


# ---------- Purchase requests ----------
class PurchaseRequestCreate(BaseModel):
    message: Optional[str] = None


class PurchaseRequestUpdate(BaseModel):
    status: RequestStatus  # seller sets this to accepted/rejected


class PurchaseRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int
    buyer_id: int
    message: Optional[str] = None
    status: RequestStatus
    created_at: datetime
