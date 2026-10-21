"""Evidence handling: copy images into the output evidence folder, hash them, and OCR them."""
from __future__ import annotations

import hashlib
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

log = logging.getLogger(__name__)

try:
    import imagehash
except ImportError:  # perceptual duplicate detection degrades to exact-hash only
    imagehash = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

TESSERACT_CANDIDATES = [
    Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
    Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
    Path.home() / "AppData/Local/Programs/Tesseract-OCR/tesseract.exe",
]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".heic"}


@dataclass
class Evidence:
    filename: str
    rel_path: str | None      # relative to the output folder; None when the file was not in the export
    sha256: str | None
    phash: str | None
    is_image: bool
    ocr_status: str           # OK | No text found | OCR unavailable | OCR failed | Not an image | File missing
    ocr_text: str


class OcrEngine:
    def __init__(self, enabled: bool, tesseract_cmd: str | None, languages: str, cache):
        self.languages = languages
        self.cache = cache
        self.available = False
        self.reason = "OCR disabled in config"
        if not enabled:
            return
        if pytesseract is None:
            self.reason = "pytesseract not installed"
            return
        cmd = Path(tesseract_cmd) if tesseract_cmd else next((p for p in TESSERACT_CANDIDATES if p.exists()), None)
        if cmd is not None:
            pytesseract.pytesseract.tesseract_cmd = str(cmd)
        try:
            pytesseract.get_tesseract_version()
            self.available = True
            self.reason = "OK"
        except Exception:
            self.reason = "Tesseract OCR engine not found (see README to install)"
        log.info("OCR: %s", self.reason)

    def read(self, path: Path, sha: str) -> tuple[str, str]:
        cached = self.cache.get_ocr(sha, self.languages)
        if cached is not None:
            return cached
        if not self.available:
            return "OCR unavailable", ""
        try:
            with Image.open(path) as im:
                im = ImageOps.exif_transpose(im).convert("L")
                if im.width < 1000:  # phone screenshots OCR better upscaled
                    scale = 1000 / im.width
                    im = im.resize((1000, int(im.height * scale)))
                im = ImageOps.autocontrast(im)
                text = pytesseract.image_to_string(im, lang=self.languages, config="--psm 6")
        except Exception as exc:
            log.warning("OCR failed for %s: %s", path.name, exc)
            return "OCR failed", ""
        text = text.strip()
        status = "OK" if text else "No text found"
        self.cache.put_ocr(sha, self.languages, status, text)
        return status, text


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def process_attachment(name: str, src: Path | None, chat_slug: str, evidence_dir: Path,
                       ocr: OcrEngine) -> Evidence:
    is_image = Path(name).suffix.lower() in IMAGE_EXTS
    if src is None or not src.exists():
        return Evidence(name, None, None, None, is_image, "File missing", "")

    sha = _sha256(src)
    dest = evidence_dir / chat_slug / name
    if not dest.exists() or _sha256(dest) != sha:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    rel = dest.relative_to(evidence_dir.parent).as_posix()

    if not is_image:
        return Evidence(name, rel, sha, None, False, "Not an image", "")

    phash = None
    if imagehash is not None:
        try:
            with Image.open(src) as im:
                phash = str(imagehash.phash(im))
        except Exception as exc:
            log.warning("Could not hash %s: %s", name, exc)
    status, text = ocr.read(src, sha)
    return Evidence(name, rel, sha, phash, True, status, text)


def phash_distance(a: str | None, b: str | None) -> int | None:
    if not a or not b or imagehash is None:
        return None
    return imagehash.hex_to_hash(a) - imagehash.hex_to_hash(b)
