from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import require_role

router = APIRouter(tags=["purchase requests"])


@router.post(
    "/listings/{listing_id}/requests",
    response_model=schemas.PurchaseRequestOut,
    status_code=201,
)
def request_to_buy(
    listing_id: int,
    req_in: schemas.PurchaseRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.RoleEnum.buyer, models.RoleEnum.admin)),
):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status != models.ListingStatus.available:
        raise HTTPException(status_code=400, detail="This item is no longer available")

    purchase_request = models.PurchaseRequest(
        listing_id=listing_id,
        buyer_id=current_user.id,
        message=req_in.message,
    )
    db.add(purchase_request)
    db.commit()
    db.refresh(purchase_request)
    return purchase_request


@router.get("/listings/{listing_id}/requests", response_model=List[schemas.PurchaseRequestOut])
def view_requests_for_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.RoleEnum.seller, models.RoleEnum.admin)),
):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if current_user.role != models.RoleEnum.admin and listing.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this listing")
    return listing.requests


@router.get("/requests/me", response_model=List[schemas.PurchaseRequestOut])
def my_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.RoleEnum.buyer, models.RoleEnum.admin)),
):
    return (
        db.query(models.PurchaseRequest)
        .filter(models.PurchaseRequest.buyer_id == current_user.id)
        .all()
    )


@router.put("/requests/{request_id}", response_model=schemas.PurchaseRequestOut)
def respond_to_request(
    request_id: int,
    update_in: schemas.PurchaseRequestUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role(models.RoleEnum.seller, models.RoleEnum.admin)),
):
    purchase_request = (
        db.query(models.PurchaseRequest).filter(models.PurchaseRequest.id == request_id).first()
    )
    if not purchase_request:
        raise HTTPException(status_code=404, detail="Request not found")

    listing = purchase_request.listing
    if current_user.role != models.RoleEnum.admin and listing.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this listing")

    purchase_request.status = update_in.status
    if update_in.status == models.RequestStatus.accepted:
        listing.status = models.ListingStatus.sold
    db.commit()
    db.refresh(purchase_request)
    return purchase_request
