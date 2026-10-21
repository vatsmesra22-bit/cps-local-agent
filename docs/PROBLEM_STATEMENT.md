# Problem statement

## Background
Eko's District Coordinators (DCs) visit SBI CSPs and must record each visit in the **SBI CSP Visit App**.
The app uses geo-fencing: a visit is accepted only when the DC's GPS position is within the allowed
radius of the CSP's registered latitude/longitude, which comes from the FIGS IT team.

## Problem
Since **22 September 2026**, DCs regularly fail to complete visits in the app because of:
- GPS not detected or not working
- the CSP's registered location being wrong or missing (lat/long needs an update)
- the app showing the DC outside the radius (e.g. "500 m away")
- the CSP not being mapped in the Visit App, or the app not opening

The DC then posts a screenshot and the CSP ID in the **"Kiosk Team Eko"** WhatsApp group, and often
does the visit offline.

## Why it matters
These complaints are spread across hundreds of chat messages. There is no single record of which CSP
had which problem on which date, or whether it was fixed. SBI has asked for a proper report. Without
one, failed visits are not tracked, repeat problems go unnoticed and pending cases are not escalated
on time.

## Situation found (22 Sep – 15 Oct 2026, group export)
- 1,471 messages in the period, containing **22 app-visit failures**
- By cause:
  - GPS not working: 7
  - CSP location needs update: 5
  - outside radius: 3
  - app/server error: 3
  - visit not completed: 2
  - CSP not in Visit App: 2
- By status: 16 pending, 1 in progress, 5 resolved; 13 pending for more than 5 days
- Most messages do not state the district, and screenshots were not included in the export

## Objective
One Excel report and one dashboard, updated automatically twice a day. They capture every app-visit
failure from WhatsApp, with:
- date and reporter
- CSP ID
- problem and distance
- photo
- status
- the next action

The team uses them to fix CSP locations, escalate pending cases and report to SBI.
