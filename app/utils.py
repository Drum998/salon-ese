from datetime import datetime, timezone
import pytz
import json

# UK timezone
UK_TZ = pytz.timezone('Europe/London')

def uk_utcnow():
    """Get current UTC time"""
    return datetime.utcnow()

def uk_now():
    """
    Get current time in UK timezone (BST in summer, GMT in winter).
    Automatically handles daylight saving time transitions.
    """
    return datetime.now(UK_TZ)

def to_uk_timezone(dt):
    """Convert datetime to UK timezone"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(UK_TZ)

def uk_timezone_strftime(dt, format_str):
    """Format datetime in UK timezone"""
    if dt is None:
        return ""
    uk_dt = to_uk_timezone(dt)
    return uk_dt.strftime(format_str)

def from_json(value):
    """Convert JSON string to Python object"""
    if value is None:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

# ============================================================================
# NEW UTILITY FUNCTIONS FOR SALON MANAGEMENT
# ============================================================================

def calculate_commission(appointment_total, commission_percentage, billing_elements, billing_method):
    """
    Calculate stylist commission based on billing method and elements
    
    Args:
        appointment_total (float): Total appointment cost
        commission_percentage (float): Stylist commission percentage
        billing_elements (list): List of BillingElement objects
        billing_method (str): 'salon_bills' or 'stylist_bills'
    
    Returns:
        float: Commission amount
    """
    if billing_method == 'salon_bills':
        # Salon bills customer, stylist gets commission percentage
        return appointment_total * (commission_percentage / 100)
    else:  # stylist_bills
        # Stylist bills customer, salon gets billing elements percentage
        salon_share = sum(element.percentage for element in billing_elements)
        return appointment_total * (salon_share / 100)

def calculate_holiday_entitlement(hours_per_week):
    """
    Calculate holiday entitlement based on UK employment law
    Standard: 5.6 weeks per year (28 days for full-time)
    
    Args:
        hours_per_week (float): Weekly working hours
    
    Returns:
        int: Holiday days entitled
    """
    if hours_per_week >= 37.5:  # Full-time
        return 28
    elif hours_per_week >= 20:  # Part-time
        return int((hours_per_week / 37.5) * 28)
    else:  # Reduced hours
        return int((hours_per_week / 37.5) * 28)

def is_salon_open(date, time, salon_settings):
    """
    Check if salon is open at given date and time
    
    Args:
        date (date): Date to check
        time (time): Time to check
        salon_settings (SalonSettings): Salon settings object
    
    Returns:
        bool: True if salon is open
    """
    if not salon_settings or not salon_settings.opening_hours:
        return False
    
    # Get day of week
    day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_name = day_names[date.weekday()]
    
    day_schedule = salon_settings.opening_hours.get(day_name, {})
    
    if day_schedule.get('closed', True):
        return False
    
    # Parse opening and closing times
    open_time_str = day_schedule.get('open', '09:00')
    close_time_str = day_schedule.get('close', '18:00')
    
    try:
        open_time = datetime.strptime(open_time_str, '%H:%M').time()
        close_time = datetime.strptime(close_time_str, '%H:%M').time()
    except ValueError:
        return False
    
    return open_time <= time <= close_time

def is_stylist_available(date, time, stylist, work_patterns):
    """
    Check if stylist is available at given date and time
    
    Args:
        date (date): Date to check
        time (time): Time to check
        stylist (User): Stylist user object
        work_patterns (list): List of WorkPattern objects for the stylist
    
    Returns:
        bool: True if stylist is available
    """
    if not work_patterns:
        return True  # No work pattern means always available
    
    # Get day of week
    day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_name = day_names[date.weekday()]
    
    # Check each work pattern
    for pattern in work_patterns:
        if not pattern.is_active:
            continue
            
        day_schedule = pattern.work_schedule.get(day_name, {})
        
        if not day_schedule.get('working', False):
            continue
        
        # Parse work times
        start_time_str = day_schedule.get('start_time', '09:00')
        end_time_str = day_schedule.get('end_time', '18:00')
        
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            continue
        
        if start_time <= time <= end_time:
            return True
    
    return False

def calculate_appointment_duration(start_time, end_time):
    """
    Calculate appointment duration in minutes
    
    Args:
        start_time (time): Start time
        end_time (time): End time
    
    Returns:
        int: Duration in minutes
    """
    if not start_time or not end_time:
        return 0
    
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    
    return end_minutes - start_minutes

def format_time_range(start_time, end_time):
    """
    Format time range for display
    
    Args:
        start_time (time): Start time
        end_time (time): End time
    
    Returns:
        str: Formatted time range
    """
    if not start_time or not end_time:
        return ""
    
    start_str = start_time.strftime('%H:%M')
    end_str = end_time.strftime('%H:%M')
    
    return f"{start_str} - {end_str}"

def get_weekday_name(date):
    """
    Get weekday name from date
    
    Args:
        date (date): Date object
    
    Returns:
        str: Weekday name
    """
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return weekday_names[date.weekday()]

def get_employment_type_display(employment_type):
    """
    Get display name for employment type
    
    Args:
        employment_type (str): Employment type
    
    Returns:
        str: Display name
    """
    display_names = {
        'employed': 'Employed',
        'self_employed': 'Self-Employed'
    }
    return display_names.get(employment_type, employment_type.title())

def get_billing_method_display(billing_method):
    """
    Get display name for billing method
    
    Args:
        billing_method (str): Billing method
    
    Returns:
        str: Display name
    """
    display_names = {
        'salon_bills': 'Salon Bills Customer',
        'stylist_bills': 'Stylist Bills Customer'
    }
    return display_names.get(billing_method, billing_method.replace('_', ' ').title()) 