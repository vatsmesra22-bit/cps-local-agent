"""Run `process.py --auto-import` at fixed times every day (used by the Docker `report` service).

    python scripts/scheduler.py                 # times from CSP_REPORT_TIMES (default 10:00,15:00), TZ from CSP_TIMEZONE
    python scripts/scheduler.py --once          # run one report now and exit

The clock is the container's local time in CSP_TIMEZONE (default Asia/Kolkata). A run that fails is logged
and the scheduler waits for the next slot; it never stops on its own.
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT = Path(__file__).resolve().parents[1]
log = logging.getLogger("scheduler")


def parse_times(spec: str) -> list[tuple[int, int]]:
    """'10:00, 15:00' -> [(10, 0), (15, 0)], sorted and de-duplicated."""
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        h, m = part.split(":")
        h, m = int(h), int(m)
        if not (0 <= h < 24 and 0 <= m < 60):
            raise ValueError(f"bad time {part!r}")
        out.add((h, m))
    if not out:
        raise ValueError("no report times given")
    return sorted(out)


def next_run(now: datetime, times: list[tuple[int, int]]) -> datetime:
    """The first slot strictly after `now` (today or tomorrow)."""
    for day in (0, 1):
        base = (now + timedelta(days=day)).replace(second=0, microsecond=0)
        for h, m in times:
            slot = base.replace(hour=h, minute=m)
            if slot > now:
                return slot
    raise AssertionError("unreachable")


def run_report() -> int:
    cmd = [sys.executable, str(PROJECT / "process.py"), "--auto-import"]
    log.info("Running: %s", " ".join(cmd))
    rc = subprocess.run(cmd, cwd=PROJECT).returncode
    log.info("Report finished with exit code %d", rc)
    return rc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--once", action="store_true", help="run one report now and exit")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")

    if args.once:
        return run_report()

    tz = ZoneInfo(os.environ.get("CSP_TIMEZONE") or "Asia/Kolkata")
    times = parse_times(os.environ.get("CSP_REPORT_TIMES") or "10:00,15:00")
    if (os.environ.get("CSP_RUN_ON_START") or "true").lower() in ("1", "true", "yes"):
        run_report()
    while True:
        now = datetime.now(tz)
        slot = next_run(now, times)
        log.info("Next report at %s", slot.strftime("%Y-%m-%d %H:%M %Z"))
        while (remaining := (slot - datetime.now(tz)).total_seconds()) > 0:
            time.sleep(min(remaining, 300))  # wake every 5 min so clock changes are picked up
        run_report()


if __name__ == "__main__":
    sys.exit(main())
