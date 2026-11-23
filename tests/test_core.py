import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from core import database as db
from core.i18n import TEXT, t
from core.knowledge import DISEASES
from core.preprocess import load_image, preprocess, quality_warnings


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    db.init_db()


def test_every_class_has_both_languages():
    assert set(DISEASES) == set(config.CLASSES)
    for d in DISEASES.values():
        for field in ("name", "part", "symptoms", "recommendation", "prevention"):
            assert d[field]["en"].strip() and d[field]["kn"].strip()


def test_every_ui_string_has_both_languages():
    for key, entry in TEXT.items():
        assert entry["en"] and entry["kn"], key
    assert len(TEXT["tips"]["en"]) == len(TEXT["tips"]["kn"])
    assert t("missing_key", "kn") == "missing_key"


def test_default_admin_and_login():
    assert db.authenticate("admin", config.DEFAULT_ADMIN_PASSWORD)["role"] == "admin"
    assert db.authenticate("admin", "wrong") is None


def test_register_login_duplicate():
    assert db.register_user("Ravi", "Ravi K", "", "secret1")
    assert not db.register_user("ravi", "Other", "", "secret2")  # case-insensitive
    assert db.authenticate("RAVI", "secret1")["name"] == "Ravi K"
    assert db.authenticate("ravi", "nope") is None


def test_passwords_not_stored_in_plain_text():
    db.register_user("sita", "Sita", "", "mypassword")
    with db.connect() as c:
        stored = c.execute("SELECT password FROM users WHERE username='sita'").fetchone()[0]
    assert "mypassword" not in stored


def test_prediction_history_and_language():
    db.register_user("ravi", "Ravi", "", "secret1")
    uid = db.authenticate("ravi", "secret1")["user_id"]
    db.save_prediction(uid, "a.jpg", "stem_bleeding", 0.9)
    en = db.get_history(uid, "en")[0]
    kn = db.get_history(uid, "kn")[0]
    assert en["disease"] == "Stem Bleeding" and kn["disease"] == "ಕಾಂಡ ರಕ್ತಸ್ರಾವ"


def test_delete_user_removes_history_but_never_admin():
    db.register_user("ravi", "Ravi", "", "secret1")
    uid = db.authenticate("ravi", "secret1")["user_id"]
    db.save_prediction(uid, "a.jpg", "healthy", 0.8)
    db.delete_user(uid)
    assert db.authenticate("ravi", "secret1") is None
    admin = db.authenticate("admin", config.DEFAULT_ADMIN_PASSWORD)
    db.delete_user(admin["user_id"])
    assert db.authenticate("admin", config.DEFAULT_ADMIN_PASSWORD)


def test_admin_can_edit_disease_info():
    raw = db.get_disease_raw("bud_borer")
    raw["recommendation"]["en"] = "Edited advice"
    db.update_disease("bud_borer", raw["symptoms"], raw["prevention"], raw["recommendation"])
    assert db.get_disease("bud_borer", "en")["recommendation"] == "Edited advice"


def test_preprocess_shape_and_quality_checks():
    rng = np.random.default_rng(0)
    sharp = rng.integers(0, 255, (300, 400, 3), dtype=np.uint8)
    assert preprocess(sharp).shape == (config.IMAGE_SIZE, config.IMAGE_SIZE, 3)
    assert "blurry" not in quality_warnings(sharp)
    assert "blurry" in quality_warnings(np.full((300, 400, 3), 128, np.uint8))
    assert "dark" in quality_warnings(np.zeros((300, 400, 3), np.uint8))


def test_load_image_handles_bad_bytes():
    assert load_image(b"not an image") is None
    ok, buf = cv2.imencode(".jpg", np.full((20, 20, 3), 200, np.uint8))
    assert load_image(buf.tobytes()).shape[:2] == (20, 20)
