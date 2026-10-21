"""Settings: defaults < config/settings.yaml < .env / environment variables < command-line overrides.

`config/settings.yaml` holds the shared business rules (date range, categories' actions, thresholds).
`.env` holds what differs per machine or person (paths, Tesseract location, the WhatsApp account lock)
and is never committed. See `.env.example` for every variable.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

try:
    from dotenv import load_dotenv
except ImportError:  # optional: plain environment variables still work
    load_dotenv = None

log = logging.getLogger(__name__)

DEFAULT_CONFIG = Path("config") / "settings.yaml"
LEGACY_CONFIG = Path("config.yaml")
DEFAULT_IMPORT_PATTERNS = ["WhatsApp Chat*.zip", "*Kiosk Team Eko*.zip", "* DC.zip"]


@dataclass
class Settings:
    project_dir: Path
    input_dir: Path
    output_dir: Path
    report_name: str
    state_db: Path
    start_date: date | None
    end_date: date | None
    timezone: str = "Asia/Kolkata"
    ocr_enabled: bool = True
    tesseract_cmd: str | None = None
    ocr_languages: str = "eng"
    bundle_minutes: int = 3
    same_csp_window_hours: int = 24
    same_text_window_hours: int = 24
    image_hash_max_distance: int = 5
    reporter_directory: Path | None = None
    watch_folder: Path | None = None
    import_patterns: list[str] = field(default_factory=lambda: list(DEFAULT_IMPORT_PATTERNS))
    visit_report_patterns: list[str] = field(default_factory=lambda: ["Visit report*.xlsx", "Visit report*.csv"])
    suggested_actions: dict[str, str] = field(default_factory=dict)
    follow_up_after_days: int = 2
    escalate_after_days: int = 5
    whatsapp_group: str = "Kiosk Team Eko"
    agent_contacts: dict[str, str] = field(default_factory=dict)
    synthetic: bool = False

    @property
    def evidence_dir(self) -> Path:
        return self.output_dir / "evidence"

    @property
    def visit_reports_dir(self) -> Path:
        return self.input_dir / "visit_reports"

    @property
    def report_path(self) -> Path:
        return self.output_dir / self.report_name


def _parse_date(value, name: str) -> date | None:
    if value in (None, "", "null"):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"{name} must be YYYY-MM-DD, got {value!r}") from exc


def _env(name: str) -> str | None:
    value = os.environ.get(name)
    return value.strip() if value and value.strip() else None


def _bool(value, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def find_config(project_dir: Path) -> Path:
    for candidate in (project_dir / DEFAULT_CONFIG, project_dir / LEGACY_CONFIG):
        if candidate.exists():
            return candidate
    return project_dir / DEFAULT_CONFIG


def load_settings(project_dir: Path, config_path: Path | None = None, **overrides) -> Settings:
    if load_dotenv is not None:
        load_dotenv(project_dir / ".env", override=False)

    config_path = config_path or find_config(project_dir)
    raw: dict = {}
    if config_path.exists():
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    else:
        log.warning("Config file %s not found; using defaults", config_path)

    dr = raw.get("date_range") or {}
    ocr = raw.get("ocr") or {}
    grouping = raw.get("grouping") or {}
    dup = raw.get("duplicates") or {}
    auto = raw.get("auto_import") or {}

    def path(override_key: str, env_key: str, yaml_value, default: str) -> Path:
        value = overrides.get(override_key) or _env(env_key) or yaml_value or default
        p = Path(value).expanduser()
        return p if p.is_absolute() else project_dir / p

    watch = _env("CSP_WATCH_FOLDER") or auto.get("watch_folder")
    reporter_dir = _env("CSP_REPORTER_DIRECTORY") or raw.get("reporter_directory")
    settings = Settings(
        project_dir=project_dir,
        input_dir=path("input_dir", "CSP_INPUT_DIR", raw.get("input_dir"), "input"),
        output_dir=path("output_dir", "CSP_OUTPUT_DIR", raw.get("output_dir"), "output"),
        report_name=overrides.get("report_name") or raw.get("report_name") or "CSP_GPS_Issue_Report.xlsx",
        state_db=path("state_db", "CSP_STATE_DB", raw.get("state_db"), "data/state.sqlite"),
        start_date=_parse_date(overrides.get("start") or _env("CSP_START_DATE") or dr.get("start"), "start date"),
        end_date=_parse_date(overrides.get("end") or _env("CSP_END_DATE") or dr.get("end"), "end date"),
        timezone=_env("CSP_TIMEZONE") or raw.get("timezone") or "Asia/Kolkata",
        ocr_enabled=_bool(_env("OCR_ENABLED"), bool(ocr.get("enabled", True))) and not overrides.get("no_ocr"),
        tesseract_cmd=_env("TESSERACT_CMD") or ocr.get("tesseract_cmd"),
        ocr_languages=_env("OCR_LANGUAGES") or ocr.get("languages") or "eng",
        bundle_minutes=int(grouping.get("bundle_minutes", 3)),
        same_csp_window_hours=int(dup.get("same_csp_window_hours", 24)),
        same_text_window_hours=int(dup.get("same_text_window_hours", 24)),
        image_hash_max_distance=int(dup.get("image_hash_max_distance", 5)),
        reporter_directory=(project_dir / reporter_dir) if reporter_dir else None,
        watch_folder=Path(watch).expanduser() if watch else None,
        import_patterns=list(auto.get("patterns") or DEFAULT_IMPORT_PATTERNS),
        visit_report_patterns=list(auto.get("visit_report_patterns") or ["Visit report*.xlsx", "Visit report*.csv"]),
        suggested_actions=dict(raw.get("suggested_actions") or {}),
        follow_up_after_days=int(raw.get("follow_up_after_days", 2)),
        escalate_after_days=int(raw.get("escalate_after_days", 5)),
        whatsapp_group=_env("WHATSAPP_GROUP_NAME") or "Kiosk Team Eko",
        agent_contacts=dict(raw.get("agent_contacts") or {}),
        synthetic=bool(overrides.get("synthetic")),
    )
    if settings.start_date and settings.end_date and settings.start_date > settings.end_date:
        raise ValueError(f"Start date {settings.start_date} is after end date {settings.end_date}")
    return settings
