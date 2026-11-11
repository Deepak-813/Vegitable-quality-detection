from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    profile_picture = Column(String(200), nullable=True)
    is_admin = Column(String(10), default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quality = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    image_path = Column(String(500), nullable=True)
    recommendation = Column(String(500), nullable=True)
    storage_days = Column(Integer, nullable=False, default=0)
    storage_temperature = Column(String(100), nullable=False, default="N/A")
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="predictions")
