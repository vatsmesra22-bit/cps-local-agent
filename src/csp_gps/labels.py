"""Plain-language names shown to the team in the dashboard and the Daily Update sheet.
The detailed tracker keeps the full category names."""

PROBLEM_NAMES = {
    "Distance Exceeds Radius": "Too far from CSP",
    "Location Mismatch (Actual vs Planned)": "Wrong location shown",
    "Location Error in Visit App": "Location error in app",
    "GPS Not Detected": "GPS not working",
    "CSP Location Needs Update": "CSP location needs update",
    "Lat/Long Incorrect or Unavailable": "Wrong latitude / longitude",
    "Location Refresh/Update Failure": "Location not updating",
    "Visit Not Completed/Updated": "Visit not done in app (offline)",
    "CSP Not in Visit App": "CSP not in visit app",
    "App/Server Error": "App / server error",
    "Other Location Issue": "Other location problem",
}

STATUS_NAMES = {
    "Open": "Pending",
    "In Progress": "Pending",
    "Escalated": "Escalated",
    "Resolved": "Solved",
    "Closed - Not an Issue": "Not a problem",
}


def problem_name(issue_type: str) -> str:
    return PROBLEM_NAMES.get(issue_type, issue_type)


def status_name(status: str) -> str:
    return STATUS_NAMES.get(status, status)
