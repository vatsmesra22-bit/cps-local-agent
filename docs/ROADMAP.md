# Roadmap – Version 2 (more agentic)

Version 1 (now) covers:
- WhatsApp exports + SBI visit reports → Excel + dashboard
- twice-daily agent run
- draft follow-ups that a human sends

Version 2 will add more features and give the agent more of the work. The ideas below are not built yet.

## Agent can see more

| Idea | Notes |
|---|---|
| Live WhatsApp Web reading | Through Claude in Chrome. Read-only, with the account lock from `.env`. Covers the group and 1:1 DC chats. |
| Read screenshots | Read error text, distance and lat/long from photos. Use OCR (Tesseract) or a vision model, and mark the result as unverified. |
| SBI visit report auto-fetch | Pick up the daily report without a manual download. |
| DC → district / CSP master list | Correct district analysis and owner per CSP. |

## Agent can act (always with approval)

| Idea | Notes |
|---|---|
| Send drafts after approval | Add an "Approve & send" button in the dashboard. Keep a log of who approved what and when. Never send automatically by default. |
| Morning summary to Ma'am | A short daily message or email built from `agent_brief.md`. |
| Weekly SBI report | A ready-to-send Excel/PDF for the SBI coordinator. |
| Official number / WABA | Move away from a personal WhatsApp when the company provides an official number. |

## Dashboard

| Idea | Notes |
|---|---|
| Edit status in the dashboard | Resolve, add a remark or reassign without opening the Excel. Changes are saved to `data/state.sqlite`. |
| Per-user login / roles | Viewer and editor roles, with an audit trail. |
| Search by CSP across all history | One page per CSP showing every complaint and visit. |

## How to add a v2 feature

1. Create a new module in `src/csp_gps/`. Add a setting that is off by default in `config/settings.yaml` or `.env.example`.
2. Hook the module into `pipeline.py` or `agent_brief.py` through one function call.
3. Add tests. Update `CHANGELOG.md` and the docs.
4. Keep the existing Excel, CSV and brief formats compatible.
