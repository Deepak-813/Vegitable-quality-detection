import os
import uuid
from PIL import Image, ImageOps
import numpy as np


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def validate_image(file_name: str) -> bool:
    return "." in file_name and file_name.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_path: str, target_size=(224, 224)) -> np.ndarray:
    image = Image.open(image_path).convert("RGB")
    image = ImageOps.fit(image, target_size, Image.Resampling.LANCZOS)
    image_array = np.array(image, dtype=np.float32) / 255.0
    return image_array


def save_uploaded_image(uploaded_file, upload_dir: str) -> str:
    os.makedirs(upload_dir, exist_ok=True)
    ext = uploaded_file.filename.rsplit(".", 1)[1].lower() if "." in uploaded_file.filename else "jpg"
    file_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(upload_dir, file_name)
    with open(file_path, "wb") as buffer:
        buffer.write(uploaded_file.file.read())
    return file_path
