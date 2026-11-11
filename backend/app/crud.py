from sqlalchemy.orm import Session
from app import models, schemas
from app.security import get_password_hash


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
        full_name=user.full_name,
        phone=user.phone,
        is_admin="false",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_prediction(db: Session, user_id: int, payload: schemas.PredictionCreate, image_path: str):
    prediction = models.Prediction(
        user_id=user_id,
        quality=payload.quality,
        confidence=payload.confidence,
        image_path=image_path,
        recommendation=payload.recommendation,
        storage_days=payload.storage_days,
        storage_temperature=payload.storage_temperature,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def get_prediction_by_id(db: Session, prediction_id: int, user_id: int):
    return db.query(models.Prediction).filter(
        models.Prediction.id == prediction_id,
        models.Prediction.user_id == user_id
    ).first()


def get_user_predictions(db: Session, user_id: int):
    return db.query(models.Prediction).filter(models.Prediction.user_id == user_id).order_by(models.Prediction.prediction_date.desc()).all()


def delete_prediction(db: Session, prediction_id: int, user_id: int):
    prediction = db.query(models.Prediction).filter(models.Prediction.id == prediction_id, models.Prediction.user_id == user_id).first()
    if prediction:
        db.delete(prediction)
        db.commit()
        return True
    return False


def admin_exists(db: Session) -> bool:
    return db.query(models.User).filter(models.User.is_admin == "true").first() is not None


def set_admin(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_admin = "true"
        db.commit()


def get_all_users(db: Session):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
