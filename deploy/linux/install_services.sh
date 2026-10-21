#!/usr/bin/env bash
# Installs and starts the systemd services (run as root):
#   csp-dashboard.service  - dashboard on port 8501, starts at boot, restarts if it stops
#   csp-report.timer       - rebuilds the report every day at 10:00 and 15:00
# Usage: sudo bash deploy/linux/install_services.sh [run-as-user]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUN_AS="${1:-${SUDO_USER:-$(whoami)}}"

for unit in csp-dashboard.service csp-report.service csp-report.timer; do
  sed -e "s#__ROOT__#${ROOT}#g" -e "s#__USER__#${RUN_AS}#g" "$ROOT/deploy/linux/$unit" > "/etc/systemd/system/$unit"
done
systemctl daemon-reload
systemctl enable --now csp-dashboard.service csp-report.timer
echo "Dashboard: http://$(hostname -I | awk '{print $1}'):8501"
echo "Status:    systemctl status csp-dashboard  |  systemctl list-timers csp-report.timer"
