import os

reports_path = r"c:\Users\DEEPAK NG\OneDrive\Desktop\vegetable-quality-detection\backend\app\routers\reports.py"
reports_content = '''from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from app.dependencies import get_current_user
from app.services.pdf_service import pdf_service

router = APIRouter(prefix="", tags=["reports"])


@router.get("/download-report/{prediction_id}")
async def download_report(prediction_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    selected = crud.get_prediction_by_id(db, prediction_id, current_user.id)
    if not selected:
        raise HTTPException(status_code=404, detail="Prediction not found")

    pdf_path = pdf_service.generate_report(current_user.username, {
        "id": selected.id,
        "quality": selected.quality,
        "confidence": selected.confidence,
        "recommendation": selected.recommendation,
        "storage_days": selected.storage_days,
        "storage_temperature": selected.storage_temperature,
    }, selected.image_path)
    return FileResponse(path=pdf_path, filename=f"report_{prediction_id}.pdf", media_type="application/pdf")
'''
with open(reports_path, "w") as f:
    f.write(reports_content)
print("reports.py written")


main_path = r"c:\Users\DEEPAK NG\OneDrive\Desktop\vegetable-quality-detection\backend\app\main.py"
main_content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import inspect, text
from app.database import Base, engine
from app.routers import auth, prediction, reports, admin
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


@app.get("/")
def read_root():
    return {"message": "AI Vegetable Quality Detection System API is running"}
'''
with open(main_path, "w") as f:
    f.write(main_content)
print("main.py written")
