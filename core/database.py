"""SQLite storage: users, plant images, predictions, diseases (matches the ER diagram)."""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

import config
from core.knowledge import DISEASES

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT UNIQUE NOT NULL,
    name      TEXT NOT NULL,
    email     TEXT,
    password  TEXT NOT NULL,
    role      TEXT NOT NULL DEFAULT 'user'
);
CREATE TABLE IF NOT EXISTS diseases (
    disease_id     TEXT PRIMARY KEY,
    disease_name   TEXT NOT NULL,
    plant_part     TEXT,
    severity       TEXT,
    symptoms       TEXT,
    prevention     TEXT,
    recommendation TEXT
);
CREATE TABLE IF NOT EXISTS plant_images (
    image_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    image_path  TEXT NOT NULL,
    upload_date TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id        INTEGER NOT NULL REFERENCES plant_images(image_id) ON DELETE CASCADE,
    disease_id      TEXT NOT NULL REFERENCES diseases(disease_id),
    confidence      REAL NOT NULL,
    prediction_date TEXT NOT NULL
);
"""

_ITERATIONS = 200_000


@contextmanager
def connect():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def _verify(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$")
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt_hex), _ITERATIONS
    )
    return hmac.compare_digest(check.hex(), digest_hex)


def init_db() -> None:
    """Create tables, seed disease info and the default admin (first run only)."""
    with connect() as conn:
        conn.executescript(SCHEMA)
        for did, d in DISEASES.items():
            exists = conn.execute(
                "SELECT 1 FROM diseases WHERE disease_id=?", (did,)
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO diseases VALUES (?,?,?,?,?,?,?)",
                    (
                        did,
                        json.dumps(d["name"], ensure_ascii=False),
                        json.dumps(d["part"], ensure_ascii=False),
                        d["severity"],
                        json.dumps(d["symptoms"], ensure_ascii=False),
                        json.dumps(d["prevention"], ensure_ascii=False),
                        json.dumps(d["recommendation"], ensure_ascii=False),
                    ),
                )
        if not conn.execute("SELECT 1 FROM users WHERE role='admin'").fetchone():
            conn.execute(
                "INSERT INTO users (username,name,email,password,role) VALUES (?,?,?,?,'admin')",
                (
                    config.DEFAULT_ADMIN_USER,
                    "Administrator",
                    "",
                    _hash(config.DEFAULT_ADMIN_PASSWORD),
                ),
            )


# ---------- users ----------
def register_user(username: str, name: str, email: str, password: str) -> bool:
    try:
        with connect() as conn:
            conn.execute(
                "INSERT INTO users (username,name,email,password) VALUES (?,?,?,?)",
                (username.strip().lower(), name.strip(), email.strip(), _hash(password)),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def authenticate(username: str, password: str):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username=?", (username.strip().lower(),)
        ).fetchone()
    if row and _verify(password, row["password"]):
        return dict(row)
    return None


def list_users():
    with connect() as conn:
        return [
            dict(r)
            for r in conn.execute(
                "SELECT user_id, username, name, email, role FROM users ORDER BY user_id"
            )
        ]


def delete_user(user_id: int) -> None:
    """Delete a non-admin user and their history."""
    with connect() as conn:
        conn.execute("DELETE FROM users WHERE user_id=? AND role!='admin'", (user_id,))


# ---------- diseases ----------
def get_disease(disease_id: str, lang: str = "en") -> dict | None:
    with connect() as conn:
        r = conn.execute(
            "SELECT * FROM diseases WHERE disease_id=?", (disease_id,)
        ).fetchone()
    if not r:
        return None

    def pick(col):
        try:
            data = json.loads(r[col])
            return data.get(lang) or data.get("en", "")
        except (TypeError, ValueError):
            return r[col]

    return {
        "disease_id": r["disease_id"],
        "name": pick("disease_name"),
        "part": pick("plant_part"),
        "severity": r["severity"],
        "symptoms": pick("symptoms"),
        "prevention": pick("prevention"),
        "recommendation": pick("recommendation"),
    }


def get_disease_raw(disease_id: str) -> dict:
    with connect() as conn:
        r = conn.execute(
            "SELECT * FROM diseases WHERE disease_id=?", (disease_id,)
        ).fetchone()
    return {
        "symptoms": json.loads(r["symptoms"]),
        "prevention": json.loads(r["prevention"]),
        "recommendation": json.loads(r["recommendation"]),
    }


def update_disease(disease_id: str, symptoms: dict, prevention: dict, recommendation: dict) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE diseases SET symptoms=?, prevention=?, recommendation=? WHERE disease_id=?",
            (
                json.dumps(symptoms, ensure_ascii=False),
                json.dumps(prevention, ensure_ascii=False),
                json.dumps(recommendation, ensure_ascii=False),
                disease_id,
            ),
        )


# ---------- images and predictions ----------
def save_prediction(user_id: int, image_path: str, disease_id: str, confidence: float) -> int:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO plant_images (user_id,image_path,upload_date) VALUES (?,?,?)",
            (user_id, image_path, now),
        )
        image_id = cur.lastrowid
        cur = conn.execute(
            "INSERT INTO predictions (image_id,disease_id,confidence,prediction_date) VALUES (?,?,?,?)",
            (image_id, disease_id, float(confidence), now),
        )
        return cur.lastrowid


def get_history(user_id: int, lang: str = "en"):
    with connect() as conn:
        rows = conn.execute(
            """SELECT p.prediction_id, p.prediction_date, p.confidence, p.disease_id,
                      i.image_path, d.disease_name, d.plant_part
               FROM predictions p
               JOIN plant_images i ON i.image_id = p.image_id
               JOIN diseases d ON d.disease_id = p.disease_id
               WHERE i.user_id = ?
               ORDER BY p.prediction_id DESC""",
            (user_id,),
        ).fetchall()
    out = []
    for r in rows:
        name = json.loads(r["disease_name"])
        part = json.loads(r["plant_part"])
        out.append(
            {
                "date": r["prediction_date"],
                "disease_id": r["disease_id"],
                "disease": name.get(lang) or name["en"],
                "part": part.get(lang) or part["en"],
                "confidence": r["confidence"],
                "image_path": r["image_path"],
            }
        )
    return out
