from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.dependencies import get_current_user
from app.security import create_access_token, verify_password
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, UPLOAD_DIR
from app.services.image_processing import validate_image
import os, uuid, shutil

router = APIRouter(prefix="", tags=["auth"])


@router.post("/register", response_model=schemas.Token)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    created_user = crud.create_user(db, user)
    access_token = create_access_token(data={"sub": created_user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
async def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, credentials.email)
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=schemas.UserOut)
async def profile(current_user=Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=schemas.UserOut)
async def update_profile(
    file: UploadFile = File(None),
    full_name: str = Form(None),
    phone: str = Form(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile (phone number, full name, or profile picture)."""
    if full_name is not None:
        current_user.full_name = full_name
    if phone is not None:
        current_user.phone = phone
    
    if file and validate_image(file.filename or ""):
        # Save profile picture
        profile_dir = os.path.join(UPLOAD_DIR, "profiles")
        os.makedirs(profile_dir, exist_ok=True)
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
        file_path = os.path.join(profile_dir, filename)
        
        # Remove old profile picture if exists
        if current_user.profile_picture:
            old_path = os.path.join(UPLOAD_DIR, current_user.profile_picture)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        current_user.profile_picture = os.path.join("profiles", filename)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/profile/picture/{user_id}")
async def get_profile_picture(user_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Serve profile picture as static file."""
    user = crud.get_user_by_id(db, user_id)
    if not user or not user.profile_picture:
        raise HTTPException(status_code=404, detail="Profile picture not found")
    
    picture_path = os.path.join(UPLOAD_DIR, user.profile_picture)
    if not os.path.exists(picture_path):
        raise HTTPException(status_code=404, detail="Profile picture not found")
    
    return FileResponse(picture_path)


@router.post("/profile/update", response_model=schemas.UserOut)
async def update_profile_info(
    full_name: str = Form(None),
    phone: str = Form(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    file: UploadFile = File(None)
):
    """Update user profile information and/or profile picture."""
    db_user = db.query(current_user.__class__).filter(current_user.__class__.id == current_user.id).first()
    
    if full_name is not None:
        db_user.full_name = full_name
    if phone is not None:
        db_user.phone = phone
    
    if file and validate_image(file.filename or ""):
        # Save profile picture
        profile_dir = os.path.join(UPLOAD_DIR, "profiles")
        os.makedirs(profile_dir, exist_ok=True)
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"user_{db_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
        file_path = os.path.join(profile_dir, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Remove old profile picture if exists
        if db_user.profile_picture:
            old_path = os.path.join(UPLOAD_DIR, db_user.profile_picture)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        
        db_user.profile_picture = os.path.join("profiles", filename)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/profile/picture", response_model=schemas.UserOut)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload or replace profile picture."""
    if not validate_image(file.filename or ""):
        raise HTTPException(status_code=400, detail="Unsupported image format. Use JPG, PNG, WebP.")
    
    # Save profile picture
    profile_dir = os.path.join(UPLOAD_DIR, "profiles")
    os.makedirs(profile_dir, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(profile_dir, filename)
    
    # Remove old profile picture if exists
    if current_user.profile_picture:
        old_path = os.path.join(UPLOAD_DIR, current_user.profile_picture)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    current_user.profile_picture = os.path.join("profiles", filename)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password reset instructions sent to your email"}


@router.post("/create-admin")
async def create_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """One-time endpoint: only works when no admin account exists yet."""
    if crud.admin_exists(db):
        raise HTTPException(status_code=403, detail="An admin account already exists. Use the database to manage admins.")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    created_user = crud.create_user(db, user)
    crud.set_admin(db, created_user.id)
    return {"message": f"Admin account created for {user.email}. You can now log in at login.html."}

