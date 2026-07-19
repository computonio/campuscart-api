import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def require_role(*allowed_roles: models.RoleEnum):
    """Usage: Depends(require_role(RoleEnum.seller, RoleEnum.admin))"""

    def checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            allowed = ", ".join(r.value for r in allowed_roles)
            raise HTTPException(
                status_code=403, detail=f"Requires one of these roles: {allowed}"
            )
        return current_user

    return checker
