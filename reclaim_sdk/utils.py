from datetime import datetime
from reclaim_sdk import RECLAIM_DATETIME_FORMAT
from datetime import datetime, timezone
from dateutil.parser import parse


def to_datetime(dt: str) -> datetime:
    """
    Parse a datetime string into a datetime object.
    """
    # Parse the datetime string
    dt = parse(dt)

    # Convert the datetime to UTC
    dt = dt.astimezone(timezone.utc)

    return dt


def from_datetime(dt: datetime) -> str:
    """
    Parse a datetime object into a string.
    """
    if not dt:
        return None
    return dt.strftime(RECLAIM_DATETIME_FORMAT)
