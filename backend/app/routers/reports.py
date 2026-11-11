from fastapi import APIRouter, Depends, HTTPException
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
