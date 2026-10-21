"""Copy new WhatsApp exports from a watch folder (e.g. Downloads) into input/.

Only files whose names match the configured patterns are copied, each file once (by content hash),
so the same export downloaded twice is not imported twice. The originals are left where they are.
"""
from __future__ import annotations

import fnmatch
import hashlib
import logging
import shutil
from pathlib import Path

log = logging.getLogger(__name__)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def import_new_exports(watch_dir: Path, patterns: list[str], input_dir: Path,
                       suffixes: tuple[str, ...] = (".zip",)) -> list[str]:
    if not watch_dir.exists():
        log.warning("Watch folder %s does not exist; nothing imported", watch_dir)
        return []
    input_dir.mkdir(parents=True, exist_ok=True)
    known = {_sha(p) for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in suffixes}
    imported: list[str] = []
    for path in sorted(watch_dir.iterdir()):
        if not path.is_file() or path.suffix.lower() not in suffixes or path.name.startswith("~$"):
            continue
        if not any(fnmatch.fnmatch(path.name.lower(), pat.lower()) for pat in patterns):
            continue
        sha = _sha(path)
        if sha in known:
            continue
        dest = input_dir / path.name
        if dest.exists():  # same name, different content: keep both
            dest = input_dir / f"{path.stem}__{sha[:8]}{path.suffix}"
        shutil.copy2(path, dest)
        known.add(sha)
        imported.append(dest.name)
        log.info("Imported new export %s", dest.name)
    return imported
