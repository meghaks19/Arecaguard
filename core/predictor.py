"""YOLO-based classifier wrapper.

Uses an Ultralytics YOLO classification model (yolov8n-cls) trained on the
folders in dataset/. If the trained weights file is missing, `available()` is
False and the app refuses to pretend: it only offers a clearly-labelled demo.
"""
from __future__ import annotations
from dataclasses import dataclass, field

import config
from core.knowledge import DISEASES
from core.preprocess import preprocess


# The bundled weights were trained on numeric folders from the current dataset.
# Their source filenames identify these labels; classes 1-4 are healthy plant parts.
NUMERIC_DATASET_CLASSES = {
    "0": "bud_borer",
    "1": "healthy",
    "2": "healthy",
    "3": "healthy",
    "4": "healthy",
    "5": "mahali_koleroga",
    "6": "stem_cracking",
    "7": "stem_bleeding",
    "8": "yellow_leaf_disease",
}


@dataclass
class Prediction:
    disease_id: str
    confidence: float
    top: list = field(default_factory=list)  # [(disease_id, confidence), ...]
    is_demo: bool = False


_model = None


def available() -> bool:
    return config.MODEL_PATH.exists()


def _load():
    global _model
    if _model is None:
        from ultralytics import YOLO  # imported lazily: heavy, and only needed here

        _model = YOLO(str(config.MODEL_PATH))
    return _model


def predict(img_bgr) -> Prediction:
    model = _load()
    result = model.predict(preprocess(img_bgr), verbose=False)[0]
    probs = result.probs
    names = result.names  # class index -> folder name
    if all(name in DISEASES for name in names.values()):
        class_map = {name: name for name in names.values()}
    elif all(str(name) in NUMERIC_DATASET_CLASSES for name in names.values()):
        class_map = {name: NUMERIC_DATASET_CLASSES[str(name)] for name in names.values()}
    else:
        unknown = sorted(str(name) for name in names.values() if name not in DISEASES)
        raise ValueError(
            "The model has unsupported class labels: " + ", ".join(unknown)
            + ". Train it with the named folders listed in config.CLASSES, or configure an explicit class mapping."
        )
    order = probs.data.argsort(descending=True).tolist()
    combined = {}
    for i, name in names.items():
        disease_id = class_map[name]
        combined[disease_id] = combined.get(disease_id, 0.0) + float(probs.data[i])
    top = sorted(combined.items(), key=lambda item: item[1], reverse=True)[:3]
    return Prediction(disease_id=top[0][0], confidence=top[0][1], top=top)


def demo_prediction() -> Prediction:
    """Fixed sample output for presentations when no model is trained. NOT a real check."""
    return Prediction(
        disease_id="mahali_koleroga",
        confidence=0.92,
        top=[("mahali_koleroga", 0.92), ("healthy", 0.05), ("bud_borer", 0.03)],
        is_demo=True,
    )
