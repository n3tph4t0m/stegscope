import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("STEGSCOPE_SECRET", os.urandom(24).hex())
    UPLOAD_FOLDER = Path(os.environ.get("STEGSCOPE_UPLOADS", BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = int(os.environ.get("STEGSCOPE_MAX_BYTES", 16 * 1024 * 1024))
    ANALYSIS_TIMEOUT = int(os.environ.get("STEGSCOPE_TIMEOUT", 25))
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp", "tiff", "tif"}
