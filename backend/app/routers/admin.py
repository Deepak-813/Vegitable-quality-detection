import os
import re
import shutil
import zipfile
import asyncio
import time
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from app.dependencies import get_current_admin_user
from app.config import MODEL_PATH, BASE_DIR
from app.services.training_service import (
    start_training, get_status, get_log_queue, prepare_dataset
)

router = APIRouter(prefix="/admin", tags=["admin"])

TRAIN_UPLOAD_DIR = "train_uploads"
TRAIN_PREPARED_DIR = "train_prepared"
TRAIN_SINGLE_UPLOAD_DIR = os.path.join(TRAIN_UPLOAD_DIR, "single_uploads")


def _sanitize_folder_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return cleaned or "unknown"


def _normalize_quality_folder(quality: str) -> str:
    quality_key = (quality or "").strip().lower()
    if quality_key in {"fresh", "ripe", "good"}:
        return "Fresh"
    if quality_key in {"moderately fresh", "moderately_fresh", "unripe", "old"}:
        return "Unripe"
    if quality_key in {"rotten", "bad", "damaged", "spoiled"}:
        return "Rotten"
    return "Fresh"


IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def _count_images(dir_path: str) -> int:
    """Recursively count image files in a directory tree."""
    total = 0
    for _root, _dirs, files in os.walk(dir_path):
        for f in files:
            if f.lower().endswith(IMAGE_EXTS):
                total += 1
    return total


def _sorted_subdirs(path: str) -> list:
    return sorted(
        e for e in os.listdir(path)
        if os.path.isdir(os.path.join(path, e))
        and not e.startswith(".") and not e.startswith("__")
    )


def _find_dataset_root(base_dir: str):
    """Return the directory whose immediate children are the vegetable class
    folders. Descends through a single wrapper folder (e.g. ``vegi``) only
    when that wrapper holds no images directly (only sub-folders)."""
    if not os.path.isdir(base_dir):
        return None
    entries = _sorted_subdirs(base_dir)
    if not entries:
        return None
    dataset_root = base_dir
    if len(entries) == 1:
        candidate = os.path.join(base_dir, entries[0])
        # A wrapper folder contains sub-folders but NO images directly inside.
        has_direct = any(
            os.path.isfile(os.path.join(candidate, e))
            and e.lower().endswith(IMAGE_EXTS)
            for e in os.listdir(candidate)
        ) if os.path.isdir(candidate) else False
        if not has_direct and _sorted_subdirs(candidate):
            dataset_root = candidate
    return dataset_root


def _resolve_train_uploads_dir():
    """Locate the directory holding the user's training images.

    Searches the current working directory and the project root so the
    endpoint works regardless of the directory the server was started from.
    Returns the resolved real path or ``None``.
    """
    project_root = os.path.dirname(BASE_DIR)  # backend/ -> project root
    candidates = [
        os.path.join(os.getcwd(), TRAIN_UPLOAD_DIR),
        os.path.join(BASE_DIR, TRAIN_UPLOAD_DIR),
        os.path.join(project_root, TRAIN_UPLOAD_DIR),
    ]
    for c in candidates:
        rp = os.path.realpath(c)
        if os.path.isdir(rp) and _count_images(rp) > 0:
            return rp
    return None


def _prepare_and_start_training(upload_dir: str, epochs: int) -> dict:
    if get_status()["running"]:
        raise HTTPException(status_code=409, detail="Training already in progress.")

    classes = prepare_dataset(upload_dir, TRAIN_PREPARED_DIR)
    if not classes:
        raise HTTPException(status_code=400, detail="No valid image folders found in uploaded data.")

    started = start_training(TRAIN_PREPARED_DIR, MODEL_PATH, epochs=min(max(epochs, 1), 50))
    if not started:
        raise HTTPException(status_code=409, detail="Training already in progress.")

    return {"message": f"Training started with {len(classes)} classes.", "classes": classes}

@router.get("/users")
async def list_users(db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    return crud.get_all_users(db)


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    deleted = crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}


@router.post("/train/upload")
async def upload_training_data(
    file: UploadFile = File(...),
    epochs: int = 15,
    current_user=Depends(get_current_admin_user),
):
    """Accept a ZIP file of training images and start training."""
    if get_status()["running"]:
        raise HTTPException(status_code=409, detail="Training already in progress.")
    if not (file.filename or "").lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Please upload a .zip file.")

    # Save and extract ZIP
    if os.path.exists(TRAIN_UPLOAD_DIR):
        shutil.rmtree(TRAIN_UPLOAD_DIR)
    os.makedirs(TRAIN_UPLOAD_DIR)

    zip_path = os.path.join(TRAIN_UPLOAD_DIR, "dataset.zip")
    with open(zip_path, "wb") as f:
        f.write(await file.read())

    # Safe extraction — reject any ZIP entry with path traversal
    abs_upload = os.path.realpath(TRAIN_UPLOAD_DIR)
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.namelist():
            dest = os.path.realpath(os.path.join(abs_upload, member))
            if not dest.startswith(abs_upload + os.sep) and dest != abs_upload:
                raise HTTPException(status_code=400, detail=f"Unsafe ZIP entry: {member}")
        z.extractall(TRAIN_UPLOAD_DIR)
    os.remove(zip_path)

    # Find the actual dataset root (skip __MACOSX and hidden folders)
    dataset_root = TRAIN_UPLOAD_DIR
    entries = [e for e in os.listdir(TRAIN_UPLOAD_DIR)
               if not e.startswith(".") and not e.startswith("__")
               and os.path.isdir(os.path.join(TRAIN_UPLOAD_DIR, e))]
    if len(entries) == 1:
        dataset_root = os.path.join(TRAIN_UPLOAD_DIR, entries[0])

    # Prepare dataset structure
    training_result = _prepare_and_start_training(dataset_root, epochs)
    return training_result


@router.post("/train/upload-single")
async def upload_single_training_image(
    file: UploadFile = File(...),
    vegetable_name: str = Form(...),
    quality: str = Form(...),
    epochs: int = Form(15),
    current_user=Depends(get_current_admin_user),
):
    """Accept a single image and add it to the training set for retraining."""
    if get_status()["running"]:
        raise HTTPException(status_code=409, detail="Training already in progress.")

    filename = (file.filename or "").lower()
    if not any(filename.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    if not vegetable_name.strip():
        raise HTTPException(status_code=400, detail="Vegetable name is required.")

    quality_folder = _normalize_quality_folder(quality)
    vegetable_folder = _sanitize_folder_name(vegetable_name)
    target_dir = os.path.join(TRAIN_SINGLE_UPLOAD_DIR, vegetable_folder, quality_folder)
    os.makedirs(target_dir, exist_ok=True)

    ext = os.path.splitext(filename)[1] or ".jpg"
    target_path = os.path.join(target_dir, f"{uuid4().hex}{ext}")
    with open(target_path, "wb") as f:
        f.write(await file.read())

    return _prepare_and_start_training(TRAIN_SINGLE_UPLOAD_DIR, epochs)


@router.post("/train/train-folder")
async def train_from_existing_folder(
    epochs: int = 15,
    current_user=Depends(get_current_admin_user),
):
    """Train the model using images already present in the 'train_uploads'
    folder (no ZIP upload required). Works with flat vegetable folders or
    quality sub-folder layouts."""
    if get_status()["running"]:
        raise HTTPException(status_code=409, detail="Training already in progress.")

    upload_root = _resolve_train_uploads_dir()
    if upload_root is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No 'train_uploads' folder with images was found. "
                "Place vegetable images in 'train_uploads/<vegetable>/*.jpg'."
            ),
        )

    dataset_root = _find_dataset_root(upload_root)
    if dataset_root is None:
        raise HTTPException(
            status_code=400,
            detail="No valid image folders found in train_uploads.",
        )
    return _prepare_and_start_training(dataset_root, epochs)


@router.get("/train/status")
async def train_status(current_user=Depends(get_current_admin_user)):
    return get_status()


@router.get("/train/logs")
async def train_logs(current_user=Depends(get_current_admin_user)):
    """Server-Sent Events stream of live training logs."""
    log_queue = get_log_queue()

    async def event_stream():
        deadline = time.time() + 7200  # 2-hour max timeout
        while time.time() < deadline:
            try:
                try:
                    line = log_queue.get_nowait()
                except Exception:
                    await asyncio.sleep(0.3)
                    continue
                yield f"data: {line}\n\n"
                if line == "__DONE__":
                    break
            except asyncio.CancelledError:
                break
        else:
            yield "data: ❌ Training timed out.\n\n"
            yield "data: __DONE__\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
