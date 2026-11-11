import base64
import csv
import io
import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Response
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.dependencies import get_current_user
from app.config import UPLOAD_DIR
from app.services.image_processing import save_uploaded_image, validate_image
from app.services.prediction_service import prediction_service

router = APIRouter(prefix="", tags=["prediction"])


@router.post("/predict", response_model=schemas.PredictionOut)
async def predict(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not validate_image(file.filename or ""):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_path = save_uploaded_image(file, UPLOAD_DIR)
    prediction_result = prediction_service.predict(file_path)

    prediction = crud.create_prediction(
        db,
        current_user.id,
        schemas.PredictionCreate(
            quality=prediction_result["quality"],
            confidence=prediction_result["confidence"],
            recommendation=prediction_result["recommendation"],
            storage_days=prediction_result["storage_days"],
            storage_temperature=prediction_result["storage_temperature"],
        ),
        file_path,
    )
    # Return the prediction plus the visual analysis (heatmap) so the
    # frontend can show *where* the rotten/spoiled regions were detected.
    return {
        "id": prediction.id,
        "quality": prediction.quality,
        "confidence": prediction.confidence,
        "recommendation": prediction.recommendation,
        "storage_days": prediction.storage_days,
        "storage_temperature": prediction.storage_temperature,
        "image_path": prediction.image_path,
        "prediction_date": prediction.prediction_date,
        "analysis_image": prediction_result.get("analysis_image"),
        "analysis_stats": prediction_result.get("analysis_stats"),
    }


@router.get("/history", response_model=list[schemas.PredictionOut])
async def history(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_user_predictions(db, current_user.id)


@router.delete("/history/{prediction_id}")
async def delete_history(prediction_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    deleted = crud.delete_prediction(db, prediction_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return {"message": "Prediction deleted"}


@router.get("/dashboard")
async def dashboard(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    predictions = crud.get_user_predictions(db, current_user.id)
    fresh_count = sum(1 for p in predictions if p.quality == "Fresh")
    moderately_fresh_count = sum(1 for p in predictions if p.quality == "Moderately Fresh")
    rotten_count = sum(1 for p in predictions if p.quality == "Rotten")
    return {
        "total_predictions": len(predictions),
        "fresh_count": fresh_count,
        "moderately_fresh_count": moderately_fresh_count,
        "rotten_count": rotten_count,
        "recent_predictions": predictions[:5],
    }


@router.get("/export-csv")
async def export_csv(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    predictions = crud.get_user_predictions(db, current_user.id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "quality", "storage_days", "storage_temperature", "confidence", "prediction_date"])
    for item in predictions:
        writer.writerow([item.id, item.quality, item.storage_days, item.storage_temperature, item.confidence, item.prediction_date])
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=predictions.csv"})

@router.post("/predict-batch", response_model=schemas.BatchPredictionResponse)
async def predict_batch(
    files: List[UploadFile] = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run quality prediction on multiple uploaded images at once and return
    the grouped results (Fresh / Moderately Fresh / Rotten)."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    items = []
    summary = {"Fresh": 0, "Moderately Fresh": 0, "Rotten": 0}
    for f in files:
        if not validate_image(f.filename or ""):
            continue
        file_path = save_uploaded_image(f, UPLOAD_DIR)
        prediction_result = prediction_service.predict(file_path, include_heatmap=True)
        prediction = crud.create_prediction(
            db,
            current_user.id,
            schemas.PredictionCreate(
                quality=prediction_result["quality"],
                confidence=prediction_result["confidence"],
                recommendation=prediction_result["recommendation"],
                storage_days=prediction_result["storage_days"],
                storage_temperature=prediction_result["storage_temperature"],
            ),
            file_path,
        )
        # Separate this image (plus its heatmap) into a quality-based folder on
        # disk so the user can browse the photos grouped by Fresh / Moderately
        # Fresh / Rotten and download every heatmap at once.
        slug = {"Fresh": "fresh", "Moderately Fresh": "moderately_fresh", "Rotten": "rotten"}.get(prediction.quality, "others")
        dest_dir = os.path.join(UPLOAD_DIR, slug)
        os.makedirs(dest_dir, exist_ok=True)

        # Persist the rot/damage heatmap PNG so the frontend can render a full
        # single-image-style detail per batch item and bundle all heatmaps
        # into one ZIP (the heatmap is built from file_path, before it moves).
        analysis_url = None
        ai = prediction_result.get("analysis_image")
        if ai and ai.startswith("data:image/png;base64,"):
            heat_name = "heatmap_" + os.path.splitext(os.path.basename(file_path))[0] + ".png"
            heat_dest = os.path.join(dest_dir, heat_name)
            try:
                with open(heat_dest, "wb") as _hf:
                    _hf.write(base64.b64decode(ai.split(",", 1)[1]))
                analysis_url = f"/uploads/{slug}/{heat_name}"
            except Exception:
                analysis_url = None

        # Move the original image into the quality folder (after the heatmap,
        # which reads file_path) and keep the DB pointer consistent.
        dest_path = os.path.join(dest_dir, os.path.basename(file_path))
        shutil.move(file_path, dest_path)
        try:
            prediction.image_path = dest_path
            db.add(prediction); db.commit(); db.refresh(prediction)
        except Exception:
            db.rollback()
        image_url = f"/uploads/{slug}/{os.path.basename(dest_path)}"

        items.append(
            schemas.BatchPredictionItem(
                quality=prediction.quality,
                confidence=prediction.confidence,
                recommendation=prediction.recommendation,
                storage_days=prediction.storage_days,
                storage_temperature=prediction.storage_temperature,
                analysis_stats=prediction_result.get("analysis_stats"),
                filename=f.filename,
                image_url=image_url,
                analysis_image=analysis_url,
                id=prediction.id,
            )
        )
        if prediction.quality in summary:
            summary[prediction.quality] += 1

    return schemas.BatchPredictionResponse(results=items, summary=summary)
