from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, require_role

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("/", response_model=schemas.ListingOut, status_code=201)
def create_listing(
    listing_in: schemas.ListingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.RoleEnum.seller, models.RoleEnum.admin)),
):
    listing = models.Listing(**listing_in.model_dump(), seller_id=current_user.id)
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/", response_model=List[schemas.ListingOut])
def browse_listings(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Listing).filter(
        models.Listing.status == models.ListingStatus.available
    )
    if category:
        query = query.filter(models.Listing.category == category)
    if max_price is not None:
        query = query.filter(models.Listing.price <= max_price)
    return query.order_by(models.Listing.created_at.desc()).all()


@router.get("/mine", response_model=List[schemas.ListingOut])
def my_listings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.RoleEnum.seller, models.RoleEnum.admin)),
):
    return db.query(models.Listing).filter(models.Listing.seller_id == current_user.id).all()


@router.get("/{listing_id}", response_model=schemas.ListingOut)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


def _get_owned_listing(listing_id: int, current_user: models.User, db: Session) -> models.Listing:
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if current_user.role != models.RoleEnum.admin and listing.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this listing")
    return listing


@router.put("/{listing_id}", response_model=schemas.ListingOut)
def update_listing(
    listing_id: int,
    update_in: schemas.ListingUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.RoleEnum.seller, models.RoleEnum.admin)),
):
    listing = _get_owned_listing(listing_id, current_user, db)
    for field, value in update_in.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}", status_code=204)
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.RoleEnum.seller, models.RoleEnum.admin)),
):
    listing = _get_owned_listing(listing_id, current_user, db)
    db.delete(listing)
    db.commit()
    return None
