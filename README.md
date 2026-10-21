# CSP GPS Complaints – Eko India Financial Services (internal)

Turns the WhatsApp messages in which DCs report that they **could not complete a CSP visit in the SBI CSP
Visit App** (GPS, location, radius, mapping, app errors) into **one Excel report** and **one dashboard**.
A scheduled AI agent refreshes both twice a day.

- What and why: [docs/PROBLEM_STATEMENT.md](docs/PROBLEM_STATEMENT.md)
- Step-by-step guide in simple Hinglish: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- How it works inside: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- What every column means: [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md)
- Put it on a company server: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

## Quick start (Windows)

1. Put this folder on a **short path**, e.g. `C:\CSP-GPS`.
2. Install **Python 3.11 or 3.12** from python.org, ticking *Add python.exe to PATH*.
3. Double-click **`Setup.bat`**. It:
   - creates `.venv` and installs the packages
   - creates `.env` from `.env.example`
   - runs the tests
   - adds a Desktop shortcut
4. Put a WhatsApp export in **Downloads**: *group → ⋮ → More → Export chat → Include media*.
5. Double-click **`Update Report.bat`**. It imports the export, builds the report and opens the dashboard.

- Excel: `output/CSP_GPS_Issue_Report.xlsx`
- Dashboard: http://csp-gps.localhost:8501

## Automatic daily updates (AI agent)

The agent prompt is in [`agent/DAILY_AGENT_TASK.md`](agent/DAILY_AGENT_TASK.md). Create it in the Claude app under *Scheduled*
with cron `0 10,15 * * *`. On each run it:

1. Reads new messages in the WhatsApp group through **Claude in Chrome**. This is read-only, and happens only
   when the logged-in WhatsApp account matches `WHATSAPP_ALLOWED_PROFILE_NAME` / `WHATSAPP_ALLOWED_PHONE_LAST4` in `.env`.
2. Runs `process.py --auto-import`, which also picks up any new export in Downloads.
3. Writes a short summary: new complaints today, what is pending, what to escalate.

Requirements: the Claude app is open, the Chrome extension is signed in, and WhatsApp Web is logged in on that PC.

## Configuration

| File | Holds | Committed? |
|---|---|---|
| `config/settings.yaml` | Shared rules: date range, OCR, grouping, duplicate windows, suggested actions, follow-up and escalation days, dashboard brand | yes |
| `.env` (from `.env.example`) | Per-PC values: folders, Tesseract path, WhatsApp account lock | **no** |
| `config/reporters.example.csv` | Optional `sender,role,district` list → copy to `config/reporters.csv` | example only |

Precedence: built-in defaults < `config/settings.yaml` < `.env` / environment < command-line flags.

## Command line

```bash
.venv\Scripts\python process.py --auto-import
```

| Option | Use |
|---|---|
| `--auto-import` | First copy new export zips from `CSP_WATCH_FOLDER` (default `~/Downloads`) into `input/` |
| `--start YYYY-MM-DD --end YYYY-MM-DD` | Override the reporting period (by original message date) |
| `--no-ocr` | Skip screenshot OCR |
| `--synthetic` | Run on the labelled test data in `samples/synthetic_input` → `output_synthetic/` |
| `-v` | Debug logging (`logs/process.log`) |

Dashboard on its own:

```bash
.venv\Scripts\python -m streamlit run dashboard/app.py
```

OCR is optional. Install [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki) to read the text inside screenshots.
Without it, photos are kept as evidence and flagged "not read by OCR".

## Development

```bash
.venv\Scripts\python -m pip install -r requirements-dev.txt
```

```bash
.venv\Scripts\python -m pytest
```

```bash
.venv\Scripts\python -m ruff check .
```

```bash
.venv\Scripts\python scripts\generate_synthetic_data.py
```

The last command regenerates the SYNTHETIC test data.

## Project layout

```
├── Setup.bat                 one-time setup on a new PC
├── Update Report.bat         one click: import exports, rebuild report, open dashboard
├── process.py                CLI entry point
├── .env.example              per-PC settings template (copy to .env)
├── pyproject.toml            project metadata, pytest and ruff config
├── requirements.txt          runtime dependencies
├── requirements-dev.txt      + pytest, ruff
├── CHANGELOG.md
├── config/
│   ├── settings.yaml         shared business rules
│   └── reporters.example.csv
├── src/csp_gps/              the package (parser, extract, pipeline, excel_report, media, state, config, autoimport)
├── dashboard/app.py          Streamlit dashboard (assets/ for the logo)
├── agent/DAILY_AGENT_TASK.md prompt for the scheduled AI agent
├── scripts/                  daily_update.bat, generate_synthetic_data.py
├── deploy/                   windows/ (Task Scheduler) and linux/ (systemd) server install
├── tests/                    pytest suite
├── docs/                     problem statement, user guide, architecture, data dictionary
├── input/                    WhatsApp exports and web captures (private, not committed)
├── output/                   Excel, CSVs, evidence photos (generated, not committed)
├── data/                     state.sqlite – stable IDs, OCR cache, team edits (keep when moving)
└── logs/
```

## Data handling

- Read-only on WhatsApp. Phone numbers are masked in every output.
- Nothing leaves the PC.
- Values not present in a message stay `Not Available`; nothing is invented.
- Possible duplicates are flagged, never deleted.
- Synthetic test data is always labelled **SYNTHETIC** and kept apart from real data.
