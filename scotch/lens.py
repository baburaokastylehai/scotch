import os, json, hashlib, hmac
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PUBLIC = json.loads((BASE/"data"/"public_lens.json").read_text())

def private_available():
    return bool(os.getenv("PRIVATE_LENS_JSON") and os.getenv("PRIVATE_LENS_CODE_HASH"))

def verify_code(code: str) -> bool:
    expected = os.getenv("PRIVATE_LENS_CODE_HASH","").lower().strip()
    if not expected or not code:
        return False
    got = hashlib.sha256(code.encode("utf-8")).hexdigest()
    return hmac.compare_digest(got, expected)

def private_lens():
    raw = os.getenv("PRIVATE_LENS_JSON")
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None

def active_lens(unlocked=False):
    if unlocked:
        private = private_lens()
        if private:
            return private
    return PUBLIC
