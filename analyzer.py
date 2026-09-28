import re
from datetime import datetime


def parse_logs(log_text: str) -> dict:
    """
    Parse raw deployment logs and extract
    timestamps, log levels, messages and errors.
    """

    events = []
    errors = []
    warnings = []

    lines = log_text.strip().splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Extract timestamp
        timestamp_match = re.search(
            r"\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}",
            line
        )

        timestamp = (
            timestamp_match.group(0)
            if timestamp_match
            else None
        )

        # Detect severity
        if "ERROR" in line.upper():
            level = "ERROR"
            errors.append(line)

        elif "WARN" in line.upper():
            level = "WARNING"
            warnings.append(line)

        elif "INFO" in line.upper():
            level = "INFO"

        else:
            level = "UNKNOWN"

        events.append({
            "timestamp": timestamp,
            "level": level,
            "message": line
        })

    # Determine overall severity
    if errors:
        severity = "HIGH"

    elif warnings:
        severity = "MEDIUM"

    else:
        severity = "LOW"

    return {
        "severity": severity,
        "total_events": len(events),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "events": events
    }