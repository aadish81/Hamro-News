from datetime import datetime, timedelta, timezone
from typing import List, Optional


def filter_last_24_hours(ts_str):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    
    try:
        # Try with timezone first
        ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        try:
            # If no timezone, parse without and assume UTC
            ts = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
            ts = ts.replace(tzinfo=timezone.utc)
        except ValueError:
            # Handle other possible formats
            raise ValueError(f"Unsupported timestamp format: {ts_str}")
    
    return ts > cutoff






def get_latest_timestamp(timestamps: List[str]) -> Optional[datetime]:
    """Returns the latest timestamp from a list"""
    for i in range(len(timestamps)):
        timestamps[i] = datetime.fromisoformat(timestamps[i])
    if not timestamps:
        return None
    latest = str(max(timestamps))
    return latest
