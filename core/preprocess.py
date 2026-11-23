"""Image preprocessing with OpenCV, plus simple photo-quality checks for farmers."""
from __future__ import annotations
import cv2
import numpy as np

import config


def load_image(data: bytes) -> np.ndarray | None:
    """Decode uploaded/camera bytes into a BGR image. Returns None if unreadable."""
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img


def quality_warnings(img: np.ndarray) -> list[str]:
    """Return keys ('blurry', 'dark') for problems that make the result less reliable."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    warnings = []
    # Variance of the Laplacian is a standard sharpness measure; low = blurry.
    small = cv2.resize(gray, (512, 512))
    if cv2.Laplacian(small, cv2.CV_64F).var() < 60:
        warnings.append("blurry")
    if gray.mean() < 45:
        warnings.append("dark")
    return warnings


def preprocess(img: np.ndarray) -> np.ndarray:
    """Resize, light denoise, and gently even out lighting.

    Kept deliberately mild: the model is trained on photos processed the same
    way (train.py calls this too), so train and predict always match.
    """
    img = cv2.resize(img, (config.IMAGE_SIZE, config.IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    img = cv2.fastNlMeansDenoisingColored(img, None, 3, 3, 7, 21)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)
