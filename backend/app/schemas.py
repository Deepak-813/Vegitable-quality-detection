from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    is_admin: str
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionBase(BaseModel):
    quality: str
    confidence: float
    recommendation: Optional[str] = None
    storage_days: int
    storage_temperature: str


class PredictionCreate(PredictionBase):
    pass


class PredictionOut(PredictionBase):
    id: int
    image_path: Optional[str] = None
    prediction_date: datetime
    analysis_image: Optional[str] = None
    analysis_stats: Optional[Dict[str, float]] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_predictions: int
    fresh_count: int
    moderately_fresh_count: int
    rotten_count: int
    recent_predictions: List[PredictionOut]


class BatchPredictionItem(BaseModel):
    quality: str
    confidence: float
    recommendation: Optional[str] = None
    storage_days: int
    storage_temperature: str
    analysis_stats: Optional[Dict[str, float]] = None
    filename: Optional[str] = None
    image_url: Optional[str] = None
    analysis_image: Optional[str] = None
    id: Optional[int] = None


class BatchPredictionResponse(BaseModel):
    results: List[BatchPredictionItem]
    summary: Dict[str, int]
