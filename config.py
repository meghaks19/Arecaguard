"""Central settings for ArecaGuard."""
from __future__ import annotations
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
MODEL_PATH = BASE_DIR / "models" / "arecaguard.pt"
DB_PATH = BASE_DIR / "arecaguard.db"

# Image size the YOLO classifier is trained and run at.
IMAGE_SIZE = 224

# Class folder names used in dataset/train/<class>/ and by the model.
# Do not rename these without also retraining the model.
CLASSES = [
    "healthy",
    "mahali_koleroga",
    "yellow_leaf_disease",
    "stem_bleeding",
    "bud_borer",
    "stem_cracking",
]

# Below this confidence the app tells the farmer the result is NOT reliable.
LOW_CONFIDENCE = 0.60
# Above this the result is shown as "likely".
HIGH_CONFIDENCE = 0.85

# Default admin created on first run. Change the password immediately.
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
