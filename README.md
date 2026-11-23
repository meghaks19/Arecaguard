# ArecaGuard

AI-based arecanut disease screening from a photo. Farmers upload or capture an image of a leaf, nut or trunk; the system predicts one of six conditions with a confidence score, shows simple advice in **English or Kannada**, and keeps a history.

Stack: Python, OpenCV, Streamlit, SQLite, Ultralytics YOLO (classification).

## Project layout

```
ArecaGuard/
├── app.py              Streamlit app (login, check, history, guide, admin)
├── prepare_dataset.py  Sort a downloaded dataset into train/val
├── train.py            Train the model from dataset/
├── config.py           Settings: classes, confidence thresholds, paths
├── core/
│   ├── database.py     SQLite: users, plant_images, predictions, diseases (the ER diagram)
│   ├── preprocess.py   OpenCV resize/denoise/lighting + blur/dark photo checks
│   ├── predictor.py    YOLO wrapper (+ clearly labelled demo mode)
│   ├── knowledge.py    Disease info and advice, English + Kannada
│   └── i18n.py         All screen text, English + Kannada
├── dataset/train|val/<class>/   Your training photos go here
├── models/arecaguard.pt         Created by train.py
├── tests/test_core.py           Unit tests (10 pass)
└── FARMER_GUIDE.md              Plain-language guide for farmers
```

## Run it

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

First login: type `admin` in the email box, password `admin123`. Farmers sign up with their email address. **Change this before sharing the app** (edit `DEFAULT_ADMIN_PASSWORD` in `config.py` before the first run, or delete `arecaguard.db` and restart).

To use it on a phone in the same Wi-Fi: `streamlit run app.py --server.address 0.0.0.0`, then open `http://<laptop-ip>:8501` on the phone.

## Train the model (required for real predictions)

The app ships **without a trained model**, so it cannot give real results yet. Until `models/arecaguard.pt` exists, the check screen says so and only offers a Demo mode whose output is stamped as sample data and is never saved.

**Using the Kaggle dataset** (kaggle.com/datasets/sumanthsadiga/arecanut-plant-disease-dataset): download it (free Kaggle login needed), extract the zip, then:

```bash
python prepare_dataset.py "C:\path\to\extracted\folder" --dry-run   # shows how folders were matched
python prepare_dataset.py "C:\path\to\extracted\folder"             # copies into dataset/train and dataset/val
python train.py --allow-missing --epochs 50
```
Numeric folders can be inferred from class names in their image filenames when all images agree. For other datasets, fix a folder with `--map "Folder Name=class_name"` (or `=skip`). To prepare the existing numeric `dataset` safely without mixing old folders into the output, use `python prepare_dataset.py dataset --output dataset_prepared`, then train with `python train.py --data dataset_prepared --allow-missing --epochs 50`. `--allow-missing` trains only the classes that have photos, so the model will not recognise a disease the dataset does not include.

1. Or collect your own photos (real arecanut photos from farms, ideally hundreds per class, varied light and angles). Put about 80% in `dataset/train/<class>/` and 20% in `dataset/val/<class>/`. Classes: `healthy`, `mahali_koleroga`, `yellow_leaf_disease`, `stem_bleeding`, `bud_borer`, `stem_cracking`.
2. `python train.py --epochs 50` (it checks image counts first and downloads the small starting weights once; internet needed for that and for pip).
3. Look at `runs/arecaguard/` (confusion matrix, accuracy). Test on photos the model never saw. Do not hand it to farmers if it confuses the dangerous classes.

Photo sources: your own farm visits, university/ICAR/CPCRI image collections, and Kaggle or Mendeley datasets if any exist for arecanut (check licences). Have an agriculture officer confirm labels, since wrongly labelled photos are the biggest cause of a bad model.

## How it is designed for farmers

- English / ಕನ್ನಡ switch on every screen, large buttons, two clear steps (photo, then check).
- Colour-coded result card with an urgency label and a plain confidence bar.
- Honest about uncertainty: under 60% confidence the app says "do not rely on this" and **withholds treatment advice**; 60-85% says confirm with an expert first.
- Warns about blurry or dark photos before checking.
- Advice stays general and sends spray choice and dose to the Horticulture officer or Krishi Vigyan Kendra.

## Before real-world use

- Have an agriculture expert review `core/knowledge.py` (or edit it live in the Admin page).
- Have a native Kannada speaker review the Kannada text.
- Note that "Bud Borer" is a pest and "Stem Cracking" often is not an infection; the model sees only the picture and can confuse look-alike problems, which is why the app always asks for expert confirmation.

## Tests

```bash
pip install pytest
python -m pytest tests -q
```

The tests cover the database, login, language completeness and photo checks. They do not cover the Streamlit screens or the trained model; try those by hand.

## Fits the synopsis

Upload/webcam input, OpenCV preprocessing, YOLO model, confidence score, recommendations, SQLite history, Streamlit dashboard, user/admin roles, and the ER entities User, Plant Image, Prediction, Disease.
