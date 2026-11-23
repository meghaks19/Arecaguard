"""Train the ArecaGuard classifier.

Put photos in dataset/train/<class>/ and dataset/val/<class>/ (see README),
then run:   python train.py --epochs 50

The best weights are copied to models/arecaguard.pt, which the app loads.
"""
from __future__ import annotations
import argparse
import shutil
import sys

import config

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def count_images():
    root = config.BASE_DIR / "dataset"
    table = {}
    for split in ("train", "val"):
        for c in config.CLASSES:
            folder = root / split / c
            table[(split, c)] = (
                sum(1 for p in folder.glob("*") if p.suffix.lower() in IMG_EXT)
                if folder.exists()
                else 0
            )
    return table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--base", default="yolov8n-cls.pt", help="starting weights (downloaded once)")
    ap.add_argument("--min-per-class", type=int, default=30)
    ap.add_argument("--allow-missing", action="store_true",
                    help="train only on classes that have photos (empty class folders are removed)")
    args = ap.parse_args()

    counts = count_images()
    print(f"{'class':22s} {'train':>6s} {'val':>6s}")
    problems = []
    for c in config.CLASSES:
        tr, va = counts[("train", c)], counts[("val", c)]
        print(f"{c:22s} {tr:6d} {va:6d}")
        if tr < args.min_per_class or va < 5:
            problems.append(c)
    if problems and args.allow_missing:
        empty = [c for c in problems if counts[("train", c)] == 0 and counts[("val", c)] == 0]
        for c in empty:
            for split in ("train", "val"):
                shutil.rmtree(config.BASE_DIR / "dataset" / split / c, ignore_errors=True)
        problems = [c for c in problems if c not in empty]
        print("\nTraining without: " + (", ".join(empty) or "(none)"))
    if problems:
        sys.exit(
            "\nNot enough images for: " + ", ".join(problems)
            + f"\nNeed at least {args.min_per_class} train and 5 val images per class "
            "(hundreds per class gives much better results)."
        )

    from ultralytics import YOLO

    model = YOLO(args.base)
    model.train(
        data=str(config.BASE_DIR / "dataset"),
        epochs=args.epochs,
        imgsz=config.IMAGE_SIZE,
        project=str(config.BASE_DIR / "runs"),
        name="arecaguard",
        exist_ok=True,
        # Augmentation helps because farm photos vary a lot in light and angle.
        hsv_v=0.4,
        degrees=15,
        fliplr=0.5,
        scale=0.3,
    )
    best = config.BASE_DIR / "runs" / "arecaguard" / "weights" / "best.pt"
    shutil.copy(best, config.MODEL_PATH)
    print(f"\nSaved model to {config.MODEL_PATH}")
    print("Check the confusion matrix in runs/arecaguard/ before trusting it with farmers.")


if __name__ == "__main__":
    main()
