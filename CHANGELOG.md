# Changelog

## 1.5.0 – 2026-10-21 – branded login, v2 ready

### Added
- New **login page**: official Eko logo + KIOSK, "Eko Bharat Ventures · Since 2007", gold "Complaints" title,
  styled password box and button.
- `CLAUDE.md`: project notes and rules for AI agents, including the version 2 plan.
- `docs/ROADMAP.md`: version 2 ideas (more agentic) and how to add a feature.

## 1.4.0 – 2026-10-21 – server deployment

### Added
- Dashboard **password login**: `DASHBOARD_PASSWORD` or `DASHBOARD_PASSWORD_SHA256` in `.env`. No password means
  open, for local use only.
- `deploy/windows/`:
  - `install_tasks.ps1` (dashboard at boot, report at 10:00/15:00, firewall rule)
  - `start_dashboard.bat`
  - `uninstall_tasks.ps1`
- `deploy/linux/`:
  - `setup.sh`, `install_services.sh`
  - systemd units `csp-dashboard.service`, `csp-report.service`, `csp-report.timer`
- `docs/DEPLOYMENT.md`: install, daily use, updates via `git pull`, backup and a security checklist.

## 1.3.0 – 2026-10-21 – agentic

### Added
- **Auto-close.** When the SBI CSP Visit App report shows a visit for the complaint's CSP on or after the
  complaint date, the agent marks the complaint Resolved and records the visit date and score as evidence.
  Statuses set by hand still win.
- **Agent brief** (`output/agent_brief.json` / `.md`) after every run:
  - what changed since the last run (new, closed, auto-closed, newly needing escalation)
  - **ready-to-send WhatsApp drafts**: a daily summary for the manager, CSP lists for tech support and the
    SBI coordinator (one line per CSP), and requests to DCs for missing CSP IDs
  - the agent never sends anything itself
- Dashboard **🤖 Agent** tab with these changes and the drafts, each with a copy button.
- The scheduled agent reads WhatsApp screenshots itself (error text, distance, lat/long) and adds them as
  `[Screenshot] …` lines, so Tesseract is no longer needed for WhatsApp Web captures. Its summary now
  reports the agent brief.
- `agent_contacts` in `config/settings.yaml` (who the drafts are addressed to).
- The dashboard refreshes itself within a minute when new data is written.
- App Visits shows the period, a visit-date filter and a date-wise table with a per-day drill-down (also in Excel).

## 1.2.0 – 2026-10-20

### Added
- **SBI CSP Visit App reports** (`Visit report*.xlsx`):
  - auto-imported to `input/visit_reports/`, written to `output/visits.csv`
  - new Excel sheet **App Visits**
  - repeated rows counted once
- Each complaint shows whether the same CSP was later visited in the app (*App Visit After Complaint*,
  *App Visit Score*). Pending complaints with such a visit get "App visit recorded – confirm and close".
- Dashboard **🗓 App Visits** tab:
  - visits, CSPs, DC users, average and low scores, compliance
  - "complaint CSPs – visited in the app or not"
  - circle, DC and score lists
  - searchable visit table
- Priority on every complaint (🔴 Escalate · 🟣 Confirm & close · 🟠 Follow up · 🔵 New · 🟢 Solved); lists are sorted by it.
- Optional `config/dc_users.csv` (`username,dc_name`) to show DC names for app usernames.

### Changed
- Dashboard: tabs moved to a top navigation bar, one font everywhere (Plus Jakarta Sans), charts replaced by
  simple ranked lists.

## 1.1.0 – 2026-10-20

### Added
- DC one-to-one chats as a source (e.g. "Anil Sharma DC.zip"); auto-import pattern `* DC.zip`.
- New category **Location Error in Visit App** ("visit location error", "location issue").
- Daily-report items marked `(Offline)` count as visits not done in the app.
- Mapping problems count as complaints: "location map", "mapping issue", "remapping".
- Several CSP codes listed above one shared request become one record per CSP.
- Dashboard:
  - 5 cards, including **Escalate now**
  - "Who reported?" chart
  - Chat and Reported-by filters
  - compact "new today" box with a full-list expander
  - district chart only for districts that were actually written
- Excel opens on a simple **Daily Update** sheet.

### Fixed
- Forwarded copies of earlier complaints (e.g. 23 messages re-forwarded on 12 Oct) are flagged as duplicates.
- "Visit done offline" no longer marks a complaint as solved.
- The exporter's own questions without a CSP code ("You: Location me aapne kya update kiya hai") are not complaints.
- An empty export is reported as "empty export – export the chat again".

### Data
- Group export up to 20 Oct and Anil Sharma DC chat. Totals:
  - 66 unique complaints (40 group, 26 Anil Sharma DC), 57 CSPs, 26 possible duplicates flagged
  - 59 pending, 52 to escalate, 7 solved
- "Vijay Maharashtra DC.zip" was empty.

## 1.0.0 – 2026-10-16

### Added
- Pipeline for WhatsApp exports:
  - Android, iOS and Web-copy formats, `.jsonl` web captures, loose images
  - reply quotes linked from `chat.md`
  - safe zip extraction
- Complaint rules tuned on the real "Kiosk Team Eko" export:
  - unlabelled CSP codes (`1A85xxxx`) and misspelt distances ("Miter")
  - multi-CSP lists split into one record per CSP
  - check-ins, notices, form fields and resolution replies excluded
  - "app visit failed" cases included
- Status from quoted replies: "Issue resolved" → Resolved, "Ok" → In Progress, plus escalation requests.
- Suggested Action, Next Step (follow up after 2 days, escalate after 5), Days Pending and Added On.
- 7-sheet Excel workbook with formulas, dropdowns, conditional formatting and charts. Team edits are kept across runs.
- Streamlit dashboard: simple language, Eko Kiosk colours, "Aaj ki nayi complaints", "What to do now", photo viewer, Excel/CSV export.
- Auto-import of new exports from Downloads; `Update Report.bat`; `scripts/daily_update.bat`.
- Scheduled agent (`agent/DAILY_AGENT_TASK.md`) at 10:00 and 15:00. It reads WhatsApp Web via Claude in Chrome, read-only, behind an account lock.
- Standard layout:
  - `config/settings.yaml` and `.env` / `.env.example`
  - `pyproject.toml`, `requirements-dev.txt`, ruff lint
  - `docs/`, `Setup.bat`
- 20 tests (parser formats, extraction rules, reply linking, end-to-end on synthetic data, workbook structure, re-run stability).

### Data
- First real run: 5,541 messages, 1,471 of them from 22 Sep–15 Oct 2026, giving 22 complaints.
