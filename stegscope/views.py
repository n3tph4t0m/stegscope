import tempfile
from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
)
from werkzeug.utils import secure_filename

from .analysis import run_all

bp = Blueprint("main", __name__)


def _allowed(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/api/analyze")
def analyze():
    upload = request.files.get("image")
    if upload is None or not upload.filename:
        return jsonify(error="No file provided."), 400

    filename = secure_filename(upload.filename)
    if not _allowed(filename):
        allowed = ", ".join(sorted(current_app.config["ALLOWED_EXTENSIONS"]))
        return jsonify(error=f"Extension not allowed. Accepted formats: {allowed}."), 400

    ext = filename.rsplit(".", 1)[1].lower()
    workdir = Path(tempfile.mkdtemp(dir=current_app.config["UPLOAD_FOLDER"]))
    stored = workdir / filename

    try:
        upload.save(stored)
        size = stored.stat().st_size
        report = run_all(stored, ext, current_app.config["ANALYSIS_TIMEOUT"])
    finally:
        for item in workdir.glob("*"):
            item.unlink(missing_ok=True)
        workdir.rmdir()

    return jsonify(filename=filename, size=size, report=report)
