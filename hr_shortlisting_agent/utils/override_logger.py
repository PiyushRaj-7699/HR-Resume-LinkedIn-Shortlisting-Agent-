"""
Override logger for audit trail of HR score adjustments.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def log_override(
    candidate_name: str,
    dimension: str,
    original_score: float,
    new_score: float,
    reason: str,
    log_file: str = "outputs/override_log.json",
) -> None:
    """
    Log an HR score override with timestamp and reason for audit trail.

    Args:
        candidate_name: Name of the candidate.
        dimension: Scoring dimension that was overridden (e.g., "skills_match").
        original_score: Original LLM-assigned score.
        new_score: New HR-assigned score.
        reason: Reason for the override.
        log_file: Path to the override log file (default: outputs/override_log.json).
    """
    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "candidate_name": candidate_name,
        "dimension": dimension,
        "original_score": original_score,
        "new_score": new_score,
        "reason": reason,
    }

    # Ensure outputs directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing log or create new
    logs = []
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Could not read existing log file {log_file}: {e}. Starting fresh.")
            logs = []

    # Append new entry and write back
    logs.append(log_entry)
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except IOError as e:
        logger.error(f"Failed to write override log to {log_file}: {e}")
        return

    # Print confirmation
    print(f"[Override Logged] {candidate_name} — {dimension}: {original_score} → {new_score}")
