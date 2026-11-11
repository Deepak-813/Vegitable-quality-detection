import os
import io
import base64
import numpy as np
from typing import Dict, Optional
from app.config import MODEL_PATH
from app.services.image_processing import preprocess_image
from PIL import Image, ImageDraw

QUALITY_LABELS = ["Fresh", "Moderately Fresh", "Rotten"]

VEGETABLE_PROFILES = {
    "Tomato":  {"hue": 8,   "hue_tol": 20, "min_sat": 0.35, "r": (150, 255), "g": (20,  110), "b": (10,  80)},
    "Carrot":  {"hue": 24,  "hue_tol": 16, "min_sat": 0.50, "r": (190, 255), "g": (90,  170), "b": (0,   50)},
    "Potato":  {"hue": 35,  "hue_tol": 25, "min_sat": 0.06, "r": (140, 220), "g": (110, 190), "b": (70,  150)},
    "Cabbage": {"hue": 108, "hue_tol": 28, "min_sat": 0.20, "r": (30,  130), "g": (100, 210), "b": (30,  120)},
}

VEGETABLE_STORAGE = {
    "Tomato":   {"Fresh": {"days": 7,  "temperature": "10-12C (Cool Pantry)"},
                  "Moderately Fresh": {"days": 3,  "temperature": "4-7C (Refrigerator)"},
                  "Rotten": {"days": 0, "temperature": "Discard immediately"}},
    "Carrot":   {"Fresh": {"days": 14, "temperature": "0-4C (Cold, humid storage)"},
                  "Moderately Fresh": {"days": 5,  "temperature": "0-4C (Refrigerator)"},
                  "Rotten": {"days": 0, "temperature": "Discard immediately"}},
    "Potato":   {"Fresh": {"days": 10, "temperature": "4-10C (Cool, dark, dry)"},
                  "Moderately Fresh": {"days": 4,  "temperature": "4-7C (Cool storage)"},
                  "Rotten": {"days": 0, "temperature": "Discard immediately"}},
    "Cabbage":  {"Fresh": {"days": 10, "temperature": "0-4C (Cold, humid storage)"},
                  "Moderately Fresh": {"days": 5,  "temperature": "0-4C (Refrigerator)"},
                  "Rotten": {"days": 0, "temperature": "Discard immediately"}},
}

DEFAULT_STORAGE = {
    "Fresh": {"days": 5, "temperature": "4-7C (Refrigerator)"},
    "Moderately Fresh": {"days": 2, "temperature": "0-4C (Cold storage)"},
    "Rotten": {"days": 0, "temperature": "Discard immediately"},
}


def _rgb_to_hsv(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    diff = mx - mn
    if mx == 0:
        return 0, 0, 0
    s = diff / mx
    v = mx
    if diff == 0:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / diff)) % 360
    elif mx == g:
        h = 60 * ((b - r) / diff) + 120
    else:
        h = 60 * ((r - g) / diff) + 240
    return h, s, v


def _rgb_to_hsv_batch(rgb):
    """Vectorised RGB -> HSV matching _rgb_to_hsv (rgb in 0..1, returns h in 0..360,
    s and v in 0..1). ``rgb`` shape: (H, W, 3)."""
    R, G, B = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    mx = np.maximum(np.maximum(R, G), B)
    mn = np.minimum(np.minimum(R, G), B)
    diff = mx - mn
    v = mx
    with np.errstate(divide="ignore", invalid="ignore"):
        s = np.where(mx == 0, 0.0, diff / np.where(mx == 0, 1.0, mx))
    h = np.zeros_like(mx, dtype=np.float64)
    nonzero = diff > 0
    mask_r = nonzero & (mx == R)
    mask_g = nonzero & (mx == G)
    mask_b = nonzero & (mx == B)
    h[mask_r] = np.mod(60.0 * ((G[mask_r] - B[mask_r]) / diff[mask_r]), 360.0)
    h[mask_g] = 60.0 * ((B[mask_g] - R[mask_g]) / diff[mask_g]) + 120.0
    h[mask_b] = 60.0 * ((R[mask_b] - G[mask_b]) / diff[mask_b]) + 240.0
    return h, s, v


def _rot_bboxes(mask, min_pixels=2):
    # Axis-aligned bounding boxes (x0, y0, x1, y1) of 8-connected components
    # in a 2-D bool mask -> used to draw green outline boxes around rot/damage.
    from collections import deque
    H, W = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    boxes = []
    for y in range(H):
        for x in range(W):
            if mask[y, x] and not seen[y, x]:
                q = deque([(y, x)]); seen[y, x] = True
                xs = [x]; ys = [y]
                while q:
                    cy, cx = q.popleft()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if dx == 0 and dy == 0:
                                continue
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not seen[ny, nx]:
                                seen[ny, nx] = True
                                q.append((ny, nx))
                                xs.append(nx); ys.append(cy)
                if len(xs) >= min_pixels:
                    boxes.append((min(xs), min(ys), max(xs), max(ys)))
    return boxes

def _analyze_image(image_path: str):
    img = Image.open(image_path).convert("RGB").resize((150, 150))
    pixels = np.array(img).reshape(-1, 3).astype(float)

    sampled = pixels[::3]
    hsv_list = [_rgb_to_hsv(p[0], p[1], p[2]) for p in sampled]
    hues = np.array([h for h, s, v in hsv_list])
    sats = np.array([s for h, s, v in hsv_list])
    vals = np.array([v for h, s, v in hsv_list])

    mean_hue = float(np.median(hues))
    mean_sat = float(np.mean(sats))
    mean_val = float(np.mean(vals))
    mean_r   = float(np.mean(pixels[:, 0]))
    mean_g   = float(np.mean(pixels[:, 1]))
    mean_b   = float(np.mean(pixels[:, 2]))

    brown_mask = (
        (pixels[:, 0] - pixels[:, 1] > 25) &
        (pixels[:, 0] > 70) & (pixels[:, 0] < 190) &
        (pixels[:, 1] < 140) & (pixels[:, 2] < 110)
    )
    brown_ratio  = float(np.mean(brown_mask))
    dark_ratio   = float(np.mean(vals < 0.22))
    yellow_ratio = float(np.mean(
        [(h > 38 and h < 68 and s > 0.28) for h, s, v in hsv_list]
    ))
    return mean_hue, mean_sat, mean_val, mean_r, mean_g, mean_b, brown_ratio, dark_ratio, yellow_ratio


def _identify_vegetable(mean_hue, mean_sat, mean_r, mean_g, mean_b):
    scores = {}
    for veg, prof in VEGETABLE_PROFILES.items():
        hue_diff = min(abs(mean_hue - prof["hue"]), 360 - abs(mean_hue - prof["hue"]))
        hue_score = max(0.0, 1.0 - hue_diff / (prof["hue_tol"] * 2))
        sat_score = 1.0 if mean_sat >= prof["min_sat"] else mean_sat / max(prof["min_sat"], 0.01)

        def chan(val, lo, hi):
            if lo <= val <= hi:
                return 1.0
            return max(0.0, 1.0 - min(abs(val - lo), abs(val - hi)) / 55.0)

        rgb_score = (chan(mean_r, *prof["r"]) + chan(mean_g, *prof["g"]) + chan(mean_b, *prof["b"])) / 3.0
        scores[veg] = hue_score * 0.40 + sat_score * 0.15 + rgb_score * 0.45

    best = max(scores, key=lambda k: scores[k])
    confidence = round(scores[best] * 100, 1)
    return best, max(confidence, 35.0)


def _determine_quality(vegetable, brown_ratio, dark_ratio, yellow_ratio, mean_val, mean_sat):
    rot_score = (brown_ratio * 60) + (dark_ratio * 80) + (yellow_ratio * 30)
    if vegetable in ("Potato", "Cabbage"):
        if rot_score > 22 or dark_ratio > 0.30:
            return "Rotten", min(92, 58 + rot_score)
        elif rot_score > 10 or mean_val < 0.30:
            return "Moderately Fresh", min(88, 52 + rot_score * 1.5)
        return "Fresh", min(95, 72 + (1 - brown_ratio - dark_ratio) * 20)
    if rot_score > 16 or dark_ratio > 0.25:
        return "Rotten", min(94, 60 + rot_score)
    elif rot_score > 7 or yellow_ratio > 0.18 or mean_val < 0.35:
        return "Moderately Fresh", min(90, 55 + rot_score * 1.5)
    return "Fresh", min(96, 74 + (1 - brown_ratio - dark_ratio) * 20)


class PredictionService:
    def __init__(self):
        self.model = None
        self.class_indices = {}
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(MODEL_PATH):
                import tensorflow as tf
                self.model = tf.keras.models.load_model(MODEL_PATH)
                indices_path = MODEL_PATH.replace(".keras", "_classes.txt")
                if os.path.exists(indices_path):
                    with open(indices_path) as f:
                        for line in f:
                            parts = line.strip().split(",", 1)
                            if len(parts) == 2:
                                self.class_indices[int(parts[0])] = parts[1]
        except Exception:
            self.model = None

    def predict(self, image_path: str, include_heatmap: bool = True) -> Dict[str, object]:
        result = self._model_predict(image_path) if (self.model is not None and self.class_indices) else self._analyze_predict(image_path)
        # Attach a visual explanation of *where* the spoilage was detected so the
        # frontend can show "on which bases it predicted". The per-pixel stats are
        # cheap to compute; the overlay image is built only when requested, which
        # keeps batch analysis of 100+ images fast.
        try:
            heat = self.generate_spoilage_heatmap(image_path, include_image=include_heatmap)
            result["analysis_image"] = heat.get("image") if include_heatmap else None
            result["analysis_stats"] = {
                "brown_ratio": heat["brown_ratio"],
                "dark_ratio": heat["dark_ratio"],
                "yellow_ratio": heat["yellow_ratio"],
                "rotten_pixel_ratio": heat["rotten_pixel_ratio"],
            }
        except Exception:
            result["analysis_image"] = None
            result["analysis_stats"] = None
        return result

    def predict_batch(self, image_paths: list) -> list:
        """Predict quality for multiple images at once.

        The heatmap image is omitted from the batch payload to keep it light,
        but the per-image quality analysis stats are still returned.
        """
        results = []
        for path in image_paths:
            try:
                res = self.predict(path, include_heatmap=True)
                res["analysis_image"] = None
                results.append({"ok": True, "result": res, "path": path})
            except Exception as exc:
                results.append({"ok": False, "error": str(exc), "path": path})
        return results

    def generate_spoilage_heatmap(self, image_path: str, include_image: bool = True) -> dict:
        """Build a color overlay highlighting detected rotten / spoilage regions.

        Reuses the brown / dark / yellow per-pixel heuristics from _analyze_image so
        the result can be drawn back onto the image: red = rot (brown/dark) pixels,
        orange/yellow = degraded pixels. The stats are always returned; the base64
        PNG `image` overlay is built only when include_image=True, so callers that
        only need the numbers (e.g. batch analysis of 100+ images) stay fast.
        """
        orig = Image.open(image_path).convert("RGB")
        max_side = 512
        w, h = orig.size
        scale = min(1.0, max_side / float(max(w, h))) if (w and h) else 1.0
        dw, dh = max(1, int(w * scale)), max(1, int(h * scale))
        disp = orig.resize((dw, dh), Image.Resampling.LANCZOS)

        arr = np.array(disp, dtype=np.float32) / 255.0  # (H, W, 3) in 0..1
        arr255 = (arr * 255.0).astype(np.int64)
        R8, G8, B8 = arr255[:, :, 0], arr255[:, :, 1], arr255[:, :, 2]

        h_hsv, s_hsv, v_hsv = _rgb_to_hsv_batch(arr)

        brown_mask = (
            ((R8 - G8) > 25)
            & (R8 > 70) & (R8 < 190)
            & (G8 < 140) & (B8 < 110)
        )
        dark_mask = v_hsv < 0.22
        yellow_mask = (h_hsv > 38) & (h_hsv < 68) & (s_hsv > 0.28)
        rot_mask = brown_mask | dark_mask

        result = {
            "brown_ratio": round(float(np.mean(brown_mask)), 4),
            "dark_ratio": round(float(np.mean(dark_mask)), 4),
            "yellow_ratio": round(float(np.mean(yellow_mask)), 4),
            "rotten_pixel_ratio": round(float(np.mean(rot_mask)), 4),
        }

        if include_image:
            # Overlay: red where rot, orange/yellow where yellow-only.
            overlay = np.zeros_like(arr)
            overlay[rot_mask] = [0.85, 0.10, 0.10]            # rot -> red
            yellow_only = yellow_mask & ~rot_mask
            overlay[yellow_only] = [0.95, 0.78, 0.10]        # degraded -> orange/yellow
            alpha = np.zeros((dh, dw), dtype=np.float32)
            alpha[rot_mask] = 0.45
            alpha[yellow_only] = 0.35
            blended = arr * (1.0 - alpha[:, :, None]) + overlay * alpha[:, :, None]
            out_arr = (np.clip(blended, 0.0, 1.0) * 255.0).astype(np.uint8)
            out_img = Image.fromarray(out_arr, "RGB").resize((w, h), Image.Resampling.BILINEAR)
            # Draw green outline boxes around each detected rot / damage region so the
            # user can see exactly where the cuts / decay are on the image.
            try:
                _d = ImageDraw.Draw(out_img)
                _sx = (w / dw) if dw else 1.0
                _sy = (h / dh) if dh else 1.0
                for (bx0, by0, bx1, by1) in _rot_bboxes(rot_mask):
                    _d.rectangle([int(round(bx0 * _sx)), int(round(by0 * _sy)), int(round(bx1 * _sx)), int(round(by1 * _sy))], outline=(0, 255, 0), width=3)
            except Exception:
                pass
            buf = io.BytesIO()
            out_img.save(buf, format="PNG")
            result["image"] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

        return result

    def _model_predict(self, image_path: str) -> Dict[str, object]:
        image_array = preprocess_image(image_path)
        image_batch = np.expand_dims(image_array, axis=0)
        probs = self.model.predict(image_batch, verbose=0)[0]
        class_index = int(np.argmax(probs))
        confidence = float(np.max(probs) * 100)

        class_name = self.class_indices.get(class_index, "")
        parts = class_name.split("_", 1)
        identified_veg = parts[0]
        quality = parts[1].replace("_", " ") if len(parts) > 1 else "Fresh"
        if quality not in QUALITY_LABELS:
            quality = "Fresh"

        if confidence < 60:
            result = self._analyze_predict(image_path)
            storage = self._get_storage_info(result["quality"])
            result["storage_days"] = storage["days"]
            result["storage_temperature"] = storage["temperature"]
            return result

        if identified_veg in ("Cabbage", "Carrot") and quality == "Fresh":
            color_result = self._analyze_predict(image_path)
            quality = color_result["quality"]
            storage = self._get_storage_info(quality, identified_veg)
        else:
            storage = self._get_storage_info(quality, identified_veg)

        return {
            "quality": quality,
            "confidence": round(confidence, 2),
            "recommendation": self._get_recommendation(quality),
            "storage_days": storage["days"],
            "storage_temperature": storage["temperature"],
        }

    def _analyze_predict(self, image_path: str) -> Dict[str, object]:
        mean_hue, mean_sat, mean_val, mean_r, mean_g, mean_b, brown_ratio, dark_ratio, yellow_ratio = _analyze_image(image_path)
        vegetable_name, veg_conf = _identify_vegetable(mean_hue, mean_sat, mean_r, mean_g, mean_b)
        quality, qual_conf = _determine_quality(vegetable_name, brown_ratio, dark_ratio, yellow_ratio, mean_val, mean_sat)
        confidence = round((veg_conf * 0.45 + qual_conf * 0.55), 2)
        storage = self._get_storage_info(quality, vegetable_name)
        return {
            "quality": quality,
            "confidence": min(confidence, 95.0),
            "recommendation": self._get_recommendation(quality),
            "storage_days": storage["days"],
            "storage_temperature": storage["temperature"],
        }

    def _get_storage_info(self, quality: str, vegetable_name: str | None = None) -> dict:
        if vegetable_name and vegetable_name in VEGETABLE_STORAGE:
            return VEGETABLE_STORAGE[vegetable_name].get(quality, DEFAULT_STORAGE.get(quality, DEFAULT_STORAGE["Fresh"]))
        return DEFAULT_STORAGE.get(quality, DEFAULT_STORAGE["Fresh"])

    def _get_recommendation(self, quality: str) -> str:
        if quality == "Fresh":
            return "Product appears fresh. Store in a cool, dry place and use within the recommended storage period shown below."
        if quality == "Moderately Fresh":
            return "Product is moderately fresh. Consume soon and keep refrigerated if possible."
        return "Product shows signs of decay. Discard immediately to avoid food waste and health risks."


prediction_service = PredictionService()