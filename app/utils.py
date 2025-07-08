from datetime import datetime
import pytz

def uk_now():
    """
    Get current time in UK timezone (BST in summer, GMT in winter).
    Automatically handles daylight saving time transitions.
    """
    uk_tz = pytz.timezone('Europe/London')
    return datetime.now(uk_tz)

def uk_utcnow():
    """
    Get current time in UK timezone and convert to UTC for database storage.
    This maintains the same interface as datetime.utcnow but uses UK time.
    """
    uk_time = uk_now()
    return uk_time.astimezone(pytz.UTC)

def to_uk_timezone(dt):
    """
    Convert a UTC datetime to UK timezone for display.
    If dt is None or naive, returns the original value.
    """
    if dt is None:
        return dt
    
    # If datetime is naive (no timezone), assume it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    
    # Convert to UK timezone
    uk_tz = pytz.timezone('Europe/London')
    return dt.astimezone(uk_tz)

def uk_timezone_strftime(dt, format_str):
    """
    Convert a UTC datetime to UK timezone and format it as a string.
    This is a template filter that combines timezone conversion and formatting.
    """
    if dt is None:
        return 'Never'
    
    uk_time = to_uk_timezone(dt)
    return uk_time.strftime(format_str) 