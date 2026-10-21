#!/usr/bin/env bash
# One-time setup on a Linux server (Ubuntu/Debian/RHEL). Run from the project folder:
#   bash deploy/linux/setup.sh
# Then install the services as root:  sudo bash deploy/linux/install_services.sh
set -euo pipefail
cd "$(dirname "$0")/../.."

PY="${PYTHON:-python3}"
"$PY" -c 'import sys; assert (3,10) <= sys.version_info[:2] <= (3,13), sys.version' \
  || { echo "Need Python 3.10-3.13 (set PYTHON=/path/to/python3.12)"; exit 1; }

[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements-dev.txt
mkdir -p input/web_capture/images input/visit_reports output data logs
[ -f .env ] || cp .env.example .env
.venv/bin/python -m pytest -q tests > logs/setup_test.log 2>&1 && echo "Tests passed." || echo "Tests failed - see logs/setup_test.log"
echo "Setup done. Edit .env (DASHBOARD_PASSWORD, CSP_WATCH_FOLDER), then: sudo bash deploy/linux/install_services.sh"
