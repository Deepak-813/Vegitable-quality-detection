from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import inspect, text
from app.database import Base, engine
from app.routers import auth, prediction, reports, admin
from app.config import UPLOAD_DIR
from app.utils.logger import logger


def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        inspector = inspect(engine)
        if "users" in inspector.get_table_names():
            existing_columns = {column["name"] for column in inspector.get_columns("users")}
            with engine.begin() as conn:
                if "full_name" not in existing_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(200)"))
                if "phone" not in existing_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20)"))
                if "profile_picture" not in existing_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(200)"))
        if "predictions" in inspector.get_table_names():
            pred_columns = {column["name"] for column in inspector.get_columns("predictions")}
            with engine.begin() as conn:
                if "vegetable_name" in pred_columns:
                    conn.execute(text("ALTER TABLE predictions DROP COLUMN vegetable_name"))
                if "storage_days" not in pred_columns:
                    conn.execute(text("ALTER TABLE predictions ADD COLUMN storage_days INTEGER DEFAULT 0"))
                if "storage_temperature" not in pred_columns:
                    conn.execute(text('ALTER TABLE predictions ADD COLUMN storage_temperature VARCHAR(100) DEFAULT "N/A"'))
        logger.info("Database tables created successfully.")
    except Exception as exc:
        logger.warning(f"Database initialization skipped: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Vegetable Quality Detection System", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router)
app.include_router(prediction.router)
app.include_router(reports.router)
app.include_router(admin.router)

from fastapi.staticfiles import StaticFiles
import os
app.mount("/uploads", StaticFiles(directory=os.path.abspath(UPLOAD_DIR)), name="uploads")


@app.get("/")
def read_root():
    return {"message": "AI Vegetable Quality Detection System API is running"}
