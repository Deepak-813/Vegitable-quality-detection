from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud
from app.security import decode_access_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials") from exc

    user = crud.get_user_by_email(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_current_admin_user(current_user=Depends(get_current_user)):
    if current_user.is_admin != "true":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
