"""Parsers for WhatsApp chat exports (.txt / .zip) and WhatsApp Web capture files (.jsonl).

Supported export line formats (Android and iOS, 12h/24h, 2- or 4-digit years):
    22/09/2026, 7:32 pm - Ravi Kumar: message
    22/09/26, 19:32 - Ravi Kumar: message
    [22/09/26, 7:32:26 PM] Ravi Kumar: message
Attachment markers:
    IMG-20260922-WA0012.jpg (file attached)
    <attached: 00000012-PHOTO-2026-09-22-19-32-26.jpg>
    <Media omitted> / image omitted
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)

INVISIBLE = dict.fromkeys(map(ord, "‎‏‪‫‬⁦⁧⁨⁩﻿"), None)
SPACES = re.compile(r"[   ]")

_DATE = r"(?P<date>\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4})"
_TIME = r"(?P<time>\d{1,2}[:.]\d{2}(?:[:.]\d{2})?(?:\s?[APap]\.?\s?[Mm]\.?)?)"
ANDROID_LINE = re.compile(rf"^{_DATE},?\s+{_TIME}\s+[-–]\s+(?P<rest>.*)$")
IOS_LINE = re.compile(rf"^\[{_DATE},?\s+{_TIME}\]\s+(?P<rest>.*)$")
# Messages copied from WhatsApp Web / Desktop: "[7:32 pm, 22/09/2026] Ravi Kumar: message"
WEB_COPY_LINE = re.compile(rf"^\[{_TIME},\s*{_DATE}\]\s+(?P<rest>.*)$")

MEDIA_EXT = r"(?:jpe?g|png|webp|gif|heic|bmp|mp4|3gp|mov|pdf|opus|ogg|m4a|aac|docx?|xlsx?)"
ANDROID_ATTACH = re.compile(rf"(?P<name>[^\s<>:\"/\\|?*][^<>:\"/\\|?*\n]*?\.{MEDIA_EXT})\s*\(file attached\)", re.I)
IOS_ATTACH = re.compile(r"<attached:\s*(?P<name>[^>]+)>", re.I)
OMITTED = re.compile(r"<media omitted>|<?\b(image|video|audio|sticker|document|GIF) omitted\b>?|"
                     r"<मीडिया (?:छोड़ दिया गया|हटा दिया गया)>", re.I)
# Placeholders that carry no content of their own.
NOISE = re.compile(r"<album message>|<unknown message>|^\s*This message was deleted\.?\s*$|^\s*You deleted this message\.?\s*$",
                   re.I | re.M)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".bmp"}


@dataclass
class Message:
    chat_name: str
    source_file: str          # path relative to the project folder
    line_no: int
    timestamp: datetime
    sender: str | None        # None for system messages
    text: str
    attachments: list[str] = field(default_factory=list)
    media_omitted: bool = False
    source_kind: str = "export"   # export | web_capture | image_only
    source_url: str | None = None  # web capture: where the message was read
    attachment_paths: dict[str, Path] = field(default_factory=dict)  # filled by media lookup
    quoted: str = ""   # "Sender: text" of the message this one replies to (from the .md export)

    @property
    def is_system(self) -> bool:
        return self.sender is None

    @property
    def msg_id(self) -> str:
        key = "|".join([self.chat_name, self.timestamp.isoformat(), self.sender or "", self.text.strip(),
                        ",".join(sorted(self.attachments))])
        return hashlib.sha1(key.encode("utf-8")).hexdigest()

    @property
    def reference(self) -> str:
        if self.source_kind == "image_only":
            return f"Image file: {self.source_file} (time from filename)"
        if self.source_kind == "web_capture":
            return f"WhatsApp Web capture: {self.chat_name} @ {self.timestamp:%Y-%m-%d %H:%M} ({self.source_file}#L{self.line_no})"
        return f"{self.source_file}#L{self.line_no}"


@dataclass
class ParseResult:
    messages: list[Message] = field(default_factory=list)
    files_ok: list[str] = field(default_factory=list)
    files_failed: list[tuple[str, str]] = field(default_factory=list)
    unparsed_lines: int = 0


def clean(text: str) -> str:
    return SPACES.sub(" ", text.translate(INVISIBLE))


def chat_name_from_path(path: Path) -> str:
    stem = path.stem
    for prefix in ("WhatsApp Chat with ", "WhatsApp Chat - ", "WhatsApp Chat with", "Chat de WhatsApp con "):
        if stem.startswith(prefix):
            return stem[len(prefix):].strip() or stem
    if stem.lower() in {"_chat", "chat"}:
        parent = path.parent.name
        for prefix in ("WhatsApp Chat - ", "WhatsApp Chat with "):
            if parent.startswith(prefix):
                return parent[len(prefix):].strip()
        return parent
    return stem


def _read_text(path: Path) -> str:
    for enc in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError("could not decode file as UTF-8, UTF-16 or CP1252")


def _detect_dayfirst(date_strings: list[str]) -> bool:
    """WhatsApp uses the phone's locale. Decide day/month order from the file's own evidence."""
    first_gt12 = second_gt12 = 0
    for d in date_strings:
        a, b, _ = re.split(r"[/.\-]", d)
        first_gt12 += int(a) > 12
        second_gt12 += int(b) > 12
    if second_gt12 and not first_gt12:
        return False
    return True  # India default, and correct whenever the first field exceeds 12


def _parse_dt(date_s: str, time_s: str, dayfirst: bool) -> datetime:
    a, b, y = (int(x) for x in re.split(r"[/.\-]", date_s))
    day, month = (a, b) if dayfirst else (b, a)
    year = y + 2000 if y < 100 else y
    t = time_s.replace(".", ":", 2) if re.match(r"^\d{1,2}\.\d{2}", time_s) else time_s
    t = re.sub(r"\s?([APap])\.?\s?[Mm]\.?$", lambda m: " " + m.group(1).upper() + "M", t.strip())
    for fmt in ("%I:%M:%S %p", "%I:%M %p", "%H:%M:%S", "%H:%M"):
        try:
            tm = datetime.strptime(t, fmt)
            return datetime(year, month, day, tm.hour, tm.minute, tm.second)
        except ValueError:
            continue
    raise ValueError(f"unrecognised time {time_s!r}")


def _split_sender(rest: str) -> tuple[str | None, str]:
    if ": " in rest:
        sender, text = rest.split(": ", 1)
        if 0 < len(sender) <= 80:
            return sender.strip(), text
    return None, rest


def _extract_attachments(text: str) -> tuple[list[str], bool, str]:
    names = [m.group("name").strip() for m in ANDROID_ATTACH.finditer(text)]
    names += [m.group("name").strip() for m in IOS_ATTACH.finditer(text)]
    omitted = bool(OMITTED.search(text))
    remaining = IOS_ATTACH.sub("", ANDROID_ATTACH.sub("", text))
    remaining = NOISE.sub("", OMITTED.sub("", remaining))
    remaining = "\n".join(line.strip() for line in remaining.splitlines() if line.strip())
    return names, omitted, remaining


def parse_export_text(content: str, chat_name: str, source_file: str) -> tuple[list[Message], int]:
    lines = clean(content).splitlines()
    heads = []
    for i, line in enumerate(lines):
        m = IOS_LINE.match(line) or WEB_COPY_LINE.match(line) or ANDROID_LINE.match(line)
        if m:
            heads.append((i, m))
    dayfirst = _detect_dayfirst([m.group("date") for _, m in heads])

    messages: list[Message] = []
    unparsed = 0
    head_idx = {i: m for i, m in heads}
    current: dict | None = None

    def flush():
        if current is None:
            return
        body = "\n".join(current["lines"])
        names, omitted, remaining = _extract_attachments(body)
        messages.append(Message(chat_name=chat_name, source_file=source_file, line_no=current["line"],
                                timestamp=current["ts"], sender=current["sender"], text=remaining,
                                attachments=names, media_omitted=omitted))

    for i, line in enumerate(lines):
        m = head_idx.get(i)
        if m:
            try:
                ts = _parse_dt(m.group("date"), m.group("time"), dayfirst)
            except ValueError as exc:
                log.debug("%s line %d: %s", source_file, i + 1, exc)
                m = None
            else:
                flush()
                sender, text = _split_sender(m.group("rest"))
                current = {"line": i + 1, "ts": ts, "sender": sender, "lines": [text]}
                continue
        if current is not None:
            current["lines"].append(line)
        elif line.strip():
            unparsed += 1
    flush()
    return messages, unparsed


def parse_web_capture(path: Path, rel: str) -> list[Message]:
    """One JSON object per line: chat, timestamp (ISO), sender, text, images (paths relative to the file), url."""
    out: list[Message] = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        rec = json.loads(line)
        images = rec.get("images") or []
        msg = Message(chat_name=rec["chat"], source_file=rel, line_no=n,
                      timestamp=datetime.fromisoformat(rec["timestamp"]).replace(tzinfo=None),
                      sender=rec.get("sender"), text=clean(rec.get("text") or ""),
                      attachments=[Path(p).name for p in images], source_kind="web_capture",
                      source_url=rec.get("url"))
        for p in images:
            candidate = (path.parent / p).resolve()
            if candidate.exists():
                msg.attachment_paths[Path(p).name] = candidate
        out.append(msg)
    return out


def _safe_extract(zip_path: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    root = dest.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            target = (dest / member.filename).resolve()
            if not str(target).startswith(str(root)):
                log.warning("Skipping unsafe path %s in %s", member.filename, zip_path.name)
                continue
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(target, "wb") as dst:
                    dst.write(src.read())


def discover_and_parse(input_dir: Path, project_dir: Path, work_dir: Path) -> ParseResult:
    result = ParseResult()
    if not input_dir.exists():
        log.error("Input directory %s does not exist", input_dir)
        return result

    for zp in sorted(input_dir.rglob("*.zip")):
        dest = work_dir / "extracted" / zp.stem
        try:
            _safe_extract(zp, dest)
            log.info("Extracted %s", zp.name)
        except (zipfile.BadZipFile, OSError) as exc:
            result.files_failed.append((_rel(zp, project_dir), f"zip extract failed: {exc}"))

    search_roots = [input_dir, work_dir / "extracted"]
    seen: set[str] = set()
    for root in search_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel = _rel(path, project_dir)
            try:
                if path.suffix.lower() == ".txt":
                    content = _read_text(path)
                    msgs, unparsed = parse_export_text(content, chat_name_from_path(path), rel)
                    if not msgs:
                        reason = ("empty export (0 messages) - export the chat again from the phone"
                                  if not content.strip() else "no WhatsApp message lines recognised")
                        result.files_failed.append((rel, reason))
                        continue
                    result.unparsed_lines += unparsed
                elif path.suffix.lower() == ".jsonl":
                    msgs = parse_web_capture(path, rel)
                else:
                    continue
            except Exception as exc:  # one bad file must not stop the run
                log.exception("Failed to parse %s", rel)
                result.files_failed.append((rel, str(exc)))
                continue
            md = path.with_suffix(".md")
            if path.suffix.lower() == ".txt" and md.exists():
                try:
                    title, linked = attach_markdown_quotes(msgs, md)
                    log.info("%s: linked %d replies to the messages they quote", md.name, linked)
                except Exception as exc:
                    log.warning("Could not read reply quotes from %s: %s", md.name, exc)
            fresh = [m for m in msgs if m.msg_id not in seen]  # same chat exported twice
            seen.update(m.msg_id for m in fresh)
            for m in fresh:
                m.attachment_paths.update(_locate_media(m, path.parent))
            result.messages.extend(fresh)
            result.files_ok.append(rel)
            log.info("Parsed %s: %d messages (%d new)", rel, len(msgs), len(fresh))
    _add_loose_images(input_dir, project_dir, result)
    result.messages.sort(key=lambda m: (m.timestamp, m.chat_name, m.line_no))
    return result


MD_DAY = re.compile(r"^## (?P<day>[A-Z][a-z]+ \d{1,2}, \d{4})\s*$")
MD_HEAD = re.compile(r"^\[(?P<time>\d{1,2}:\d{2}(?:\s?[AP]M)?)\] \*\*(?P<sender>.+?):\*\*\s?(?P<rest>.*)$")
MD_TITLE = re.compile(r"^# WhatsApp Chat Export:\s*(?P<title>.+?)\s*$")


def _norm(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower()).strip()


def attach_markdown_quotes(messages: list[Message], md_path: Path) -> tuple[str | None, int]:
    """Some exporters write a .md next to the .txt in which replies carry the message they quote:

        [10:50 AM] **+91 96676 05718:**
        > _Sakshi Office: @~Amit singh 1A851811  GPS Issue_
        Ok

    The .txt loses that link, so it is copied onto the matching .txt message (same day, minute,
    sender and reply text). Returns the chat title from the .md header and the number linked.
    """
    lines = clean(md_path.read_text(encoding="utf-8")).splitlines()
    title = None
    entries: list[tuple[datetime, str, str, str]] = []
    day = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if (t := MD_TITLE.match(line)):
            title = t.group("title")
        elif (d := MD_DAY.match(line)):
            day = datetime.strptime(d.group("day"), "%B %d, %Y").date()
        elif day and (h := MD_HEAD.match(line)):
            tm = datetime.strptime(h.group("time").replace(" ", ""), "%I:%M%p" if "M" in h.group("time") else "%H:%M")
            j = i + 1
            quote: list[str] = []
            if not h.group("rest") and j < len(lines) and lines[j].startswith("> _"):
                while j < len(lines):
                    quote.append(lines[j])
                    if lines[j].rstrip().endswith("_"):
                        j += 1
                        break
                    j += 1
                body = []
                while j < len(lines) and lines[j].strip() and not MD_HEAD.match(lines[j]) and not MD_DAY.match(lines[j]):
                    body.append(lines[j])
                    j += 1
                q = "\n".join(quote)
                q = re.sub(r"^> _", "", q).rstrip()
                q = q[:-1] if q.endswith("_") else q
                entries.append((datetime.combine(day, tm.time()), h.group("sender"), q, "\n".join(body)))
                i = j
                continue
        i += 1

    by_key: dict[tuple, list[Message]] = {}
    for m in messages:
        by_key.setdefault((m.timestamp.replace(second=0), m.sender), []).append(m)
    linked = 0
    for ts, sender, quote, body in entries:
        candidates = by_key.get((ts, sender), [])
        nb = _norm(body)[:40]
        match = next((m for m in candidates if not m.quoted and _norm(m.text).startswith(nb)), None)
        if match is None and len(candidates) == 1 and not candidates[0].quoted:
            match = candidates[0]
        if match is not None:
            match.quoted = quote
            linked += 1
    if title:
        for m in messages:
            m.chat_name = title
    return title, linked


LOOSE_IMAGE_TS = [
    # WhatsApp Image 2026-09-22 at 19.37.25.jpeg / ... at 7.32.26 PM.jpeg
    (re.compile(r"(\d{4})-(\d{2})-(\d{2}) at (\d{1,2})\.(\d{2})\.(\d{2})(?:\s*([AP]M))?", re.I), "wa"),
    # IMG-20260922-WA0012.jpg (date only)
    (re.compile(r"IMG-(\d{4})(\d{2})(\d{2})-WA\d+", re.I), "img"),
    # Screenshot_20260922-193725 / Screenshot_2026-09-22-19-37-25
    (re.compile(r"Screenshot_(\d{4})-?(\d{2})-?(\d{2})[-_](\d{2})-?(\d{2})-?(\d{2})", re.I), "shot"),
]


def timestamp_from_filename(name: str) -> datetime | None:
    for pat, kind in LOOSE_IMAGE_TS:
        m = pat.search(name)
        if not m:
            continue
        g = m.groups()
        y, mo, d = int(g[0]), int(g[1]), int(g[2])
        if kind == "img":
            return datetime(y, mo, d)
        h, mi, s = int(g[3]), int(g[4]), int(g[5])
        if kind == "wa" and g[6]:
            h = h % 12 + (12 if g[6].upper() == "PM" else 0)
        return datetime(y, mo, d, h, mi, s)
    return None


def _add_loose_images(input_dir: Path, project_dir: Path, result: ParseResult) -> None:
    """Images placed in input/ without a chat export become image-only messages (always flagged for review)."""
    linked = {p.resolve() for m in result.messages for p in m.attachment_paths.values()}
    export_dirs = {(project_dir / f).resolve().parent for f in result.files_ok}
    for path in sorted(input_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS or path.resolve() in linked:
            continue
        if path.resolve().parent in export_dirs:
            continue  # media that belongs to an export but was never referenced in its chat
        rel = _rel(path, project_dir)
        ts = timestamp_from_filename(path.name)
        if ts is None:
            result.files_failed.append((rel, "image-only file has no date in its name; original time unknown"))
            continue
        msg = Message(chat_name="Image only (no chat context)", source_file=rel, line_no=0, timestamp=ts,
                      sender="Unknown (image only)", text="", attachments=[path.name], source_kind="image_only")
        msg.attachment_paths[path.name] = path
        result.messages.append(msg)


_media_index: dict[Path, dict[str, Path]] = {}


def _locate_media(msg: Message, folder: Path) -> dict[str, Path]:
    if folder not in _media_index:
        _media_index[folder] = {p.name.lower(): p for p in folder.rglob("*") if p.is_file()}
    index = _media_index[folder]
    return {name: index[name.lower()] for name in msg.attachments
            if name not in msg.attachment_paths and name.lower() in index}


def _rel(path: Path, project_dir: Path) -> str:
    try:
        return path.resolve().relative_to(project_dir.resolve()).as_posix()
    except ValueError:
        return path.name
