"""
Training service — runs in a background thread.
Accepts a prepared directory path and streams log lines into a shared queue.
"""

import os
import shutil
import threading
import queue

# Global state
_train_queue: queue.Queue = queue.Queue()
_train_status: dict = {"running": False, "done": False, "error": None}
_train_lock = threading.Lock()

QUALITY_MAP = {
    "ripe": "Fresh", "fresh": "Fresh", "good": "Fresh",
    "unripe": "Moderately_Fresh", "old": "Moderately_Fresh",
    "damaged": "Rotten", "rotten": "Rotten", "bad": "Rotten", "spoiled": "Rotten",
}
IMG_SIZE = (224, 224)
BATCH_SIZE = 32


def get_status() -> dict:
    return dict(_train_status)


def get_log_queue() -> queue.Queue:
    return _train_queue


def _log(msg: str):
    _train_queue.put(msg)


def prepare_dataset(upload_dir: str, prepared_dir: str) -> list:
    """Reorganise uploaded images into prepared/VegetableName_Quality/ folders."""
    if os.path.exists(prepared_dir):
        shutil.rmtree(prepared_dir)
    os.makedirs(prepared_dir)

    classes_found = []
    for veg_folder in sorted(os.listdir(upload_dir)):
        veg_path = os.path.join(upload_dir, veg_folder)
        if not os.path.isdir(veg_path):
            continue
        veg_name = veg_folder.strip().title()
        subdirs = [d for d in os.listdir(veg_path) if os.path.isdir(os.path.join(veg_path, d))]

        if subdirs:
            for quality_folder in subdirs:
                quality_key = quality_folder.strip().lower()
                quality_label = QUALITY_MAP.get(quality_key, "Fresh")
                class_name = f"{veg_name}_{quality_label}"
                out_dir = os.path.join(prepared_dir, class_name)
                os.makedirs(out_dir, exist_ok=True)
                src = os.path.join(veg_path, quality_folder)
                count = 0
                for img in os.listdir(src):
                    if img.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                        shutil.copy(os.path.join(src, img), os.path.join(out_dir, f"{quality_folder}_{img}"))
                        count += 1
                if count:
                    classes_found.append(class_name)
        else:
            class_name = f"{veg_name}_Fresh"
            out_dir = os.path.join(prepared_dir, class_name)
            os.makedirs(out_dir, exist_ok=True)
            count = 0
            for img in os.listdir(veg_path):
                if img.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    shutil.copy(os.path.join(veg_path, img), os.path.join(out_dir, img))
                    count += 1
            if count:
                classes_found.append(class_name)

    return sorted(set(classes_found))


def _run_training(prepared_dir: str, model_out: str, epochs: int):
    global _train_status
    try:
        import tensorflow as tf
        from tensorflow.keras import layers, Model
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.preprocessing.image import ImageDataGenerator

        _log("Loading dataset...")
        gen = ImageDataGenerator(
            rescale=1.0 / 255,
            validation_split=0.2,
            rotation_range=20,
            width_shift_range=0.1,
            height_shift_range=0.1,
            horizontal_flip=True,
            zoom_range=0.15,
        )
        train_data = gen.flow_from_directory(
            prepared_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE,
            class_mode="categorical", subset="training", shuffle=True,
        )
        val_data = gen.flow_from_directory(
            prepared_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE,
            class_mode="categorical", subset="validation", shuffle=False,
        )
        num_classes = len(train_data.class_indices)
        _log(f"Classes ({num_classes}): {list(train_data.class_indices.keys())}")
        _log(f"Train samples: {train_data.samples} | Val samples: {val_data.samples}")

        # Build model
        base = MobileNetV2(input_shape=(*IMG_SIZE, 3), include_top=False, weights="imagenet")
        base.trainable = False
        inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
        x = base(inputs, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(256, activation="relu")(x)
        x = layers.Dropout(0.3)(x)
        outputs = layers.Dense(num_classes, activation="softmax")(x)
        model = Model(inputs, outputs)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(1e-3),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )

        class LogCallback(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                logs = logs or {}
                _log(f"[Phase 1] Epoch {epoch+1}/{epochs} — loss: {logs.get('loss', 0):.4f} | acc: {logs.get('accuracy', 0)*100:.1f}% | val_acc: {logs.get('val_accuracy', 0)*100:.1f}%")

        _log(f"\nPhase 1: Training top layers ({epochs} epochs)...")
        model.fit(
            train_data, validation_data=val_data, epochs=epochs,
            callbacks=[
                LogCallback(),
                tf.keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True),
            ],
            verbose=0,
        )

        # Fine-tune
        _log("\nPhase 2: Fine-tuning last 30 layers...")
        base.trainable = True
        for layer in base.layers[:-30]:
            layer.trainable = False
        model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
                      loss="categorical_crossentropy", metrics=["accuracy"])

        class LogCallback2(tf.keras.callbacks.Callback):
            def on_epoch_end(self, epoch, logs=None):
                logs = logs or {}
                _log(f"[Phase 2] Epoch {epoch+1}/10 — loss: {logs.get('loss', 0):.4f} | acc: {logs.get('accuracy', 0)*100:.1f}% | val_acc: {logs.get('val_accuracy', 0)*100:.1f}%")

        model.fit(
            train_data, validation_data=val_data, epochs=10,
            callbacks=[
                LogCallback2(),
                tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
            ],
            verbose=0,
        )

        # Save
        model_dir = os.path.dirname(os.path.abspath(model_out))
        os.makedirs(model_dir, exist_ok=True)
        model.save(model_out)
        _log(f"\nModel saved: {model_out}")

        indices_path = model_out.replace(".keras", "_classes.txt")
        with open(indices_path, "w") as f:
            for cls, idx in sorted(train_data.class_indices.items(), key=lambda x: x[1]):
                f.write(f"{idx},{cls}\n")
        _log(f"Class map saved: {indices_path}")

        _, acc = model.evaluate(val_data, verbose=0)
        _log(f"\n✅ Training complete! Final val accuracy: {acc * 100:.2f}%")

        # Reload the prediction service with new model
        try:
            from app.services.prediction_service import prediction_service
            prediction_service._load_model()
            _log("✅ Prediction service reloaded with new model.")
        except Exception as e:
            _log(f"⚠️ Could not reload prediction service: {e}")

        _train_status["done"] = True
        _train_status["error"] = None

    except Exception as e:
        _log(f"\n❌ Training failed: {e}")
        _train_status["error"] = str(e)
    finally:
        _train_status["running"] = False
        _log("__DONE__")


def start_training(prepared_dir: str, model_out: str, epochs: int = 15) -> bool:
    """Start training in background thread. Returns False if already running."""
    with _train_lock:
        if _train_status["running"]:
            return False
        _train_status["running"] = True
        _train_status["done"] = False
        _train_status["error"] = None
        # Drain old queue
        while not _train_queue.empty():
            try:
                _train_queue.get_nowait()
            except queue.Empty:
                break

    thread = threading.Thread(target=_run_training, args=(prepared_dir, model_out, epochs), daemon=True)
    thread.start()
    return True
