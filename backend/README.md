# AI-Based Vegetable Quality Detection System

## Overview
This project provides a complete FastAPI + PostgreSQL + Bootstrap web application for vegetable quality detection using an AI-based image classifier.

## Features
- JWT authentication
- User registration/login/profile
- Image upload and prediction
- PDF report export
- Dashboard analytics
- Admin panel

## Backend
- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT authentication
- ReportLab

## Frontend
- HTML, CSS, Bootstrap 5
- Responsive animated UI
- Dark/light theme support

## Setup
1. Create a PostgreSQL database named vegetable_quality.
2. Copy backend/.env.example to backend/.env and update credentials.
3. Install Python dependencies: pip install -r backend/requirements.txt
4. Start the API: uvicorn app.main:app --reload --app-dir backend
5. Open frontend pages in a browser.

## Notes
A trained model file is expected at `backend/trained_model/vegetable_quality_model.keras`. The current implementation includes a fallback prediction path so the app can run even before a real trained model is available.

## Training the Model
Training uses transfer learning on **MobileNetV2** (Phase 1: top-layer training for `epochs` epochs, then Phase 2: fine-tuning the last 30 layers for 10 epochs). It writes both the `.keras` model and a `<name>_classes.txt` class map used by the prediction service.

### 1. From the existing `train_uploads` folder (recommended)
Images already placed in `train_uploads` are trained directly — no ZIP upload or admin login required:

```bash
# From the project root
python backend/train_from_folder.py --epochs 15
```

Or from the Admin web UI: open `frontend/admin.html`, log in as an admin, and click **"📁 Train from Existing Folder"** in the *Train Model* section. Live training logs stream into the log panel.

> The script backs up the previous model to `vegetable_quality_model.backup.keras` before overwriting it.

### 2. ZIP upload (Admin page)
Click **🚀 Start Training**, pick a `.zip`, and choose the epoch count. Required layout:

```
Vegetable/Fresh/*.jpg
Vegetable/Rotten/*.jpg
Carrot/*.jpg            # flat images are treated as "Fresh"
```

### 3. Single image (Admin page)
Use **"📸 Add Single Image"** to add one photo (choose the vegetable and quality) and trigger retraining.

### Expected `train_uploads` layout
```
train_uploads/
  vegi/
    Cabbage/*.jpg
    Carrot/*.jpg
    Potato/*.jpg
    Tomato/*.jpg            # flat  ->  <Vegetable>_Fresh class
    Tomato/Fresh/*.jpg      # quality sub-folders also supported
    Tomato/Rotten/*.jpg
```

Quality sub-folder names map to: `fresh / ripe / good` → **Fresh**, `unripe / old` → **Moderately Fresh**, `rotten / bad / damaged / spoiled` → **Rotten**.

### Running the API
```bash
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```
Open `frontend/admin.html` (Admin) to train via the UI, or `frontend/predict.html` to run predictions.
