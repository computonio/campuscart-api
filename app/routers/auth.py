from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, security

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Anyone can self-register as a buyer or seller. (Admin accounts are
    seeded separately - see main.py - not created through this endpoint,
    so a random visitor can't grant themselves admin.)"""
    if user_in.role == models.RoleEnum.admin:
        raise HTTPException(status_code=400, detail="Cannot self-register as admin")

    existing = (
        db.query(models.User)
        .filter(
            (models.User.email == user_in.email)
            | (models.User.username == user_in.username)
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already taken")

    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=security.hash_password(user_in.password),
        role=user_in.role,
        hostel=user_in.hostel,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs in with either username or email in the 'username' form field."""
    user = (
        db.query(models.User)
        .filter(
            (models.User.username == form_data.username)
            | (models.User.email == form_data.username)
        )
        .first()
    )
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = security.create_access_token({"sub": str(user.id)})
    return {"access_token": token}
