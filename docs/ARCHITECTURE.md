# Architecture

## Flow

```
 WhatsApp group "Kiosk Team Eko"
        │
        ├── (a) Phone export (.zip with chat.txt [+ chat.md] [+ media]) ──► ~/Downloads ──┐
        │                                                                                  │ --auto-import
        └── (b) WhatsApp Web, read by the scheduled agent via Claude in Chrome ──► input/web_capture/*.jsonl
                                                                                           │
                                                                                     input/  ◄┘
                                                                                           │
   process.py ──► parser ──► bundling ──► media/OCR ──► extract ──► duplicates ──► status ──► next step
                                                                                           │
                         output/CSP_GPS_Issue_Report.xlsx  ·  output/issues.csv  ·  output/evidence/
                                                                                           │
                                                          dashboard/app.py (Streamlit, port 8501)
```

The scheduled agent (`agent/DAILY_AGENT_TASK.md`, 10:00 and 15:00) does step (b), then runs
`process.py --auto-import`, then writes a short summary. Without the Chrome extension it still
processes whatever exports are in Downloads.

## Modules (`src/csp_gps/`)

| Module | Responsibility |
|---|---|
| `config.py` | Builds `Settings`: defaults < `config/settings.yaml` < `.env` / environment < CLI flags |
| `autoimport.py` | Copies new export zips from the watch folder into `input/`, once per content hash |
| `parser.py` | Parses Android, iOS and WhatsApp Web copy formats; `.jsonl` web captures; loose images (time from filename). Links reply quotes from the `.md` export. Safe zip extraction |
| `media.py` | Copies evidence into `output/evidence/`, SHA-256 and perceptual hash, Tesseract OCR with cache |
| `extract.py` | Relevance rules, issue categories, CSP ID / distance / district / coordinates extraction, phone masking |
| `pipeline.py` | Groups caption + photos, splits multi-CSP lists, flags duplicates, infers status from replies, plans next step, writes outputs |
| `excel_report.py` | The 7-sheet workbook: live formulas, dropdowns, conditional formatting, charts |
| `state.py` | SQLite (`data/state.sqlite`): stable record IDs, OCR cache, manual edits harvested from the workbook, run log |

`process.py` is the CLI. `dashboard/app.py` only reads `output/` and never writes.

## Key rules

**What counts as a complaint.** A DC wanted to do a CSP visit in the app and could not. A message is relevant when it has:
- a strong GPS/geo word (GPS, lat/long, coordinates, radius, distance, "X m away", geo-fencing), or
- a failed or offline visit ("visit nahi ho pa raha", "unable to do visit", "offline visit"), or
- an app failure tied to a visit or CSP code ("not map in visit app", "app nahi open ho raha"), or
- a bare "location" together with a problem word ("update location", "location add karna hai").

These are excluded:
- DC travel check-ins ("Leaving/Live location ...")
- office notices and `@all` broadcasts
- form fields ("Location. Siswa awwal")
- "coordinate" used as a verb
- resolution replies

**Issue type.** The first matching category, in this priority order:
1. Distance Exceeds Radius
2. Location Mismatch
3. GPS Not Detected
4. CSP Location Needs Update
5. Lat/Long Incorrect
6. Location Refresh/Update Failure
7. Visit Not Completed
8. CSP Not in Visit App
9. App/Server Error
10. Other

All matches are kept in *All Issue Categories*.

**Grouping.**
- A sender's caption and the photos sent within 3 minutes are one record.
- A reply to one's own message joins that record.
- Two quick messages about different CSP codes stay separate.
- A numbered list covering several CSPs becomes one record per CSP.

**Duplicates.** Flagged, never deleted. A record is a possible duplicate when it has:
- the same image file,
- a near-identical screenshot of the same CSP within 72 h,
- the same CSP ID and issue type within 24 h, or
- the same text within 24 h.

**Status.**
- A reply that quotes the complaint decides it: "Issue resolved" means Resolved, "Ok" means In Progress, and an escalation request means Escalated.
- Without a quote, the complaint is Resolved when the same CSP is later reported "visit done", or when the same reporter confirms a fix within 48 h. This is marked *verify*.
- Everything else is Open.
- Manual edits in the workbook always win.

**Next step.** The action text comes from `suggested_actions` in `config/settings.yaml`. The urgency comes from the age:
- 2 days: follow up
- 5 days: escalate

**Facts vs. inference.**
- Fields are filled only from explicit evidence; *Field Sources* records Message or Screenshot OCR.
- Missing values are `Not Available`, and a blank distance means "not reported", never zero.
- Every record keeps its message reference, e.g. `chat.txt#L7347`.

## Repeatability

- A record's ID is keyed by the hash of its first message, plus the list item number for multi-CSP lists.
- The same message coming from several exports is merged by message hash, so re-running never creates duplicate rows.
- Before regenerating, the run reads back Resolution Status, Assigned To and Resolution Notes from the existing workbook.

## Privacy

- Phone numbers are masked in all outputs.
- Data stays on the PC.
- The agent is read-only on WhatsApp, opens only the configured group, and only when the logged-in account matches the lock in `.env`.
