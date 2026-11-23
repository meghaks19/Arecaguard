"""Sort a downloaded image dataset into dataset/train and dataset/val.

Usage:
    python prepare_dataset.py "C:\\path\\to\\extracted\\kaggle\\folder"

It finds every folder that contains images, treats the folder name as the
class, matches it to one of ArecaGuard's six classes by keywords, and copies
about 80% of the photos to train and 20% to val.

Run it first with --dry-run to see how folders were matched. Fix any wrong or
missing match with --map, for example:
    python prepare_dataset.py SRC --map "Mahali Koleroga=mahali_koleroga" --map "Leaf Spot=skip"
Folders named only with numbers work too: --map "3=bud_borer" applies to every folder
named 3 (for example both train/3 and val/3); use --map "train/3=bud_borer" for just one.
Use =skip to ignore a folder. Original files are never changed or deleted.
"""
from __future__ import annotations

import argparse
import random
import re
import shutil
import sys
from pathlib import Path

import config

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Keywords (matched against the folder name, lowercase, letters only).
AUTO = {
    "healthy": ["healthy", "normal"],
    "mahali_koleroga": ["mahali", "koleroga", "fruitrot", "nutrot", "kole"],
    "yellow_leaf_disease": ["yellowleaf", "yellowing", "yld", "yellow"],
    "stem_bleeding": ["bleeding", "stembleed"],
    "bud_borer": ["budborer", "borer", "bud"],
    "stem_cracking": ["crack", "split"],
}


def norm(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower())


def auto_match(folder_name: str) -> str | None:
    n = norm(folder_name)
    for cls, words in AUTO.items():
        if any(w in n for w in words):
            return cls
    return None


def find_class_folders(src: Path) -> dict[Path, list[Path]]:
    found = {}
    for d in [src, *[p for p in src.rglob("*") if p.is_dir()]]:
        imgs = [f for f in d.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXT]
        if imgs:
            found[d] = imgs
    return found


def infer_class(folder: Path, images: list[Path]) -> str | None:
    """Match by folder name, then by image filenames for numeric class folders."""
    direct = auto_match(folder.name)
    if direct:
        return direct
    if not folder.name.isdigit():
        return None

    inferred = {auto_match(image.stem) for image in images}
    inferred.discard(None)
    # Do not guess if labels embedded in filenames disagree or are incomplete.
    if len(inferred) == 1 and all(auto_match(image.stem) for image in images):
        return inferred.pop()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--map", action="append", default=[], help='"folder name=class" or "folder name=skip"')
    ap.add_argument("--val-split", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--output", type=Path, default=config.BASE_DIR / "dataset",
                    help="destination dataset directory (default: dataset)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.source.is_dir():
        sys.exit(f"Folder not found: {args.source}")
    source = args.source.resolve()
    output = args.output.resolve()
    if source == output or source in output.parents or output in source.parents:
        sys.exit("Source and output folders must not overlap. For the existing dataset, use --output dataset_prepared.")

    manual = {}
    for m in args.map:
        if "=" not in m:
            sys.exit(f'Bad --map "{m}". Use "folder name=class".')
        k, v = m.rsplit("=", 1)
        if v != "skip" and v not in config.CLASSES:
            sys.exit(f'Unknown class "{v}". Choose from: {", ".join(config.CLASSES)} or skip.')
        manual[k.strip().lower()] = v

    folders = find_class_folders(args.source)
    if not folders:
        sys.exit("No images found. Check that you extracted the zip and gave the right folder.")

    plan: dict[str, list[Path]] = {c: [] for c in config.CLASSES}
    print(f"{'folder':40s} {'images':>7s}  ->  class")
    for d, imgs in sorted(folders.items()):
        rel = d.relative_to(args.source).as_posix() if d != args.source else "."
        cls = manual.get(rel.lower(), manual.get(d.name.lower(), infer_class(d, imgs)))
        shown = cls or "UNMATCHED (ignored)"
        print(f"{rel[:40]:40s} {len(imgs):7d}  ->  {shown}")
        if cls and cls != "skip":
            plan[cls].extend(imgs)

    print("\nClass totals:")
    for c in config.CLASSES:
        print(f"  {c:22s} {len(plan[c]):6d}")
    missing = [c for c in config.CLASSES if not plan[c]]
    if missing:
        print("\nNo photos for: " + ", ".join(missing))
        print("Train with:  python train.py --allow-missing   (the model will only know the classes that have photos)")
    if args.dry_run:
        print("\nDry run only: nothing copied.")
        return

    rng = random.Random(args.seed)
    root = output
    copied = 0
    for cls, files in plan.items():
        files = sorted(set(files))
        rng.shuffle(files)
        n_val = max(1, int(len(files) * args.val_split)) if len(files) > 1 else 0
        for i, f in enumerate(files):
            split = "val" if i < n_val else "train"
            out = root / split / cls
            out.mkdir(parents=True, exist_ok=True)
            # prefix with the source folder so equal file names never overwrite each other
            shutil.copy2(f, out / f"{norm(f.parent.name)}_{f.name}")
            copied += 1
    print(f"\nCopied {copied} images into {root}")


if __name__ == "__main__":
    main()
