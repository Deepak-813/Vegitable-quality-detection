from pathlib import Path
from typing import List, Tuple

from PIL import Image
import numpy as np


VEGETABLES = ["Tomato", "Potato", "Onion", "Carrot", "Brinjal", "Capsicum", "Cabbage", "Cauliflower", "Cucumber", "Beans"]
QUALITY_LABELS = ["Fresh", "Moderately Fresh", "Rotten"]


def build_training_dataset(data_dir: str) -> Tuple[np.ndarray, np.ndarray]:
    """Create a simple dataset loader for a future real training pipeline.

    Expected folder structure:
    data_dir/<vegetable>/<quality>/<image files>
    """
    data_path = Path(data_dir)
    samples = []
    labels = []

    for vegetable in VEGETABLES:
        for quality in QUALITY_LABELS:
            folder = data_path / vegetable / quality
            if not folder.exists():
                continue
            for image_file in folder.glob("*.*"):
                try:
                    image = Image.open(image_file).convert("RGB")
                    image = image.resize((224, 224))
                    samples.append(np.array(image, dtype=np.float32) / 255.0)
                    labels.append((VEGETABLES.index(vegetable) * len(QUALITY_LABELS)) + QUALITY_LABELS.index(quality))
                except Exception:
                    continue

    if not samples:
        raise FileNotFoundError("No training images were found. Place images in structured folders to train the model.")

    return np.array(samples), np.array(labels)


def build_transfer_learning_model(input_shape=(224, 224, 3), num_classes=30):
    """Create a MobileNetV2-based transfer learning model skeleton."""
    try:
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.layers import Dense, Dropout, Flatten
        from tensorflow.keras.models import Model
    except ImportError as exc:  # pragma: no cover - runtime dependency may be absent
        raise ImportError("TensorFlow is required to build and train the model") from exc

    base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=input_shape)
    base_model.trainable = False

    x = Flatten()(base_model.output)
    x = Dense(128, activation="relu")(x)
    x = Dropout(0.2)(x)
    outputs = Dense(num_classes, activation="softmax")(x)

    return Model(inputs=base_model.input, outputs=outputs)
