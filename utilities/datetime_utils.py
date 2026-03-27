from datetime import datetime, timedelta


DB_UTC_OFFSET_HOURS = 3


def format_db_datetime_local(value: str) -> str:
    try:
        if "T" in value:
            dt = datetime.fromisoformat(value)
        else:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        dt = dt + timedelta(hours=DB_UTC_OFFSET_HOURS)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return str(value)
