from app.models import SalonSettings, WorkPattern, Appointment
from datetime import datetime, date, time, timedelta
from app.extensions import db
import calendar
import logging

logger = logging.getLogger(__name__)

class SalonHoursService:
    """Service for managing salon opening hours and appointment time validation"""
    
    @staticmethod
    def get_salon_settings():
        """Get current salon settings"""
        settings = SalonSettings.query.first()
        if not settings:
            # Create default settings if none exist
            settings = SalonSettings(
                salon_name="Salon ESE",
                opening_hours={
                    'monday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'tuesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'wednesday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'thursday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'friday': {'open': '09:00', 'close': '18:00', 'closed': False},
                    'saturday': {'open': '09:00', 'close': '17:00', 'closed': False},
                    'sunday': {'open': '10:00', 'close': '16:00', 'closed': True}
                },
                emergency_extension_enabled=True
            )
            db.session.add(settings)
            db.session.commit()
        return settings
    
    @staticmethod
    def get_day_name(date_obj):
        """Get day name from date object"""
        return date_obj.strftime('%A').lower()
    
    @staticmethod
    def get_opening_hours_for_date(appointment_date):
        """Get opening hours for a specific date"""
        settings = SalonHoursService.get_salon_settings()
        day_name = SalonHoursService.get_day_name(appointment_date)
        
        if day_name not in settings.opening_hours:
            return None
        
        day_hours = settings.opening_hours[day_name]
        if day_hours.get('closed', False):
            return None
        
        try:
            open_time = datetime.strptime(day_hours['open'], '%H:%M').time()
            close_time = datetime.strptime(day_hours['close'], '%H:%M').time()
            return {
                'open': open_time,
                'close': close_time,
                'closed': False
            }
        except (ValueError, KeyError):
            return None
    
    @staticmethod
    def is_within_opening_hours(appointment_date, start_time, end_time):
        """Check if appointment time is within salon opening hours"""
        hours = SalonHoursService.get_opening_hours_for_date(appointment_date)
        if not hours:
            return False
        
        # Check if start time is before opening
        if start_time < hours['open']:
            return False
        
        # Check if end time is after closing
        if end_time > hours['close']:
            return False
        
        return True
    
    @staticmethod
    def is_emergency_extension_allowed():
        """Check if emergency extensions are enabled"""
        settings = SalonHoursService.get_salon_settings()
        return settings.emergency_extension_enabled
    
    @staticmethod
    def generate_available_time_slots(appointment_date, stylist_id=None, interval_minutes=5):
        """Generate available time slots for a given date"""
        hours = SalonHoursService.get_opening_hours_for_date(appointment_date)
        if not hours:
            return []
        
        # Get stylist work pattern if provided
        work_pattern = None
        if stylist_id:
            work_pattern = WorkPattern.query.filter_by(
                user_id=stylist_id,
                is_active=True
            ).first()
        
        # Generate time slots
        slots = []
        current_time = hours['open']
        close_time = hours['close']
        
        while current_time < close_time:
            # Check if stylist is available at this time
            if work_pattern:
                day_name = SalonHoursService.get_day_name(appointment_date)
                if not SalonHoursService._is_stylist_available_at_time(work_pattern, day_name, current_time):
                    current_time = SalonHoursService._add_minutes(current_time, interval_minutes)
                    continue
            
            # Check for existing appointments
            if not SalonHoursService._has_conflicting_appointment(appointment_date, current_time, stylist_id):
                slots.append(current_time.strftime('%H:%M'))
            
            current_time = SalonHoursService._add_minutes(current_time, interval_minutes)
        
        return slots
    
    @staticmethod
    def _is_stylist_available_at_time(work_pattern, day_name, time_obj):
        """Check if stylist is available at specific time"""
        if not work_pattern.work_schedule or day_name not in work_pattern.work_schedule:
            return False
        
        day_schedule = work_pattern.work_schedule[day_name]
        if not day_schedule.get('working', False):
            return False
        
        try:
            start_time = datetime.strptime(day_schedule['start'], '%H:%M').time()
            end_time = datetime.strptime(day_schedule['end'], '%H:%M').time()
            
            return start_time <= time_obj < end_time
        except (ValueError, KeyError):
            return False
    
    @staticmethod
    def _has_conflicting_appointment(appointment_date, start_time, stylist_id):
        """Check if there's a conflicting appointment"""
        # Calculate end time (assuming 30-minute default slot)
        end_time = SalonHoursService._add_minutes(start_time, 30)
        
        conflict = Appointment.query.filter(
            Appointment.stylist_id == stylist_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status.in_(['confirmed', 'completed']),
            db.or_(
                db.and_(
                    Appointment.start_time <= start_time,
                    Appointment.end_time > start_time
                ),
                db.and_(
                    Appointment.start_time < end_time,
                    Appointment.end_time >= end_time
                ),
                db.and_(
                    Appointment.start_time >= start_time,
                    Appointment.end_time <= end_time
                )
            )
        ).first()
        
        return conflict is not None
    
    @staticmethod
    def _add_minutes(time_obj, minutes):
        """Add minutes to a time object"""
        datetime_obj = datetime.combine(date.today(), time_obj)
        new_datetime = datetime_obj + timedelta(minutes=minutes)
        return new_datetime.time()
    
    @staticmethod
    def validate_appointment_time(appointment_date, start_time, end_time, stylist_id=None, allow_emergency=False):
        """Validate if appointment time is acceptable"""
        # Check if within opening hours
        if not SalonHoursService.is_within_opening_hours(appointment_date, start_time, end_time):
            if not allow_emergency or not SalonHoursService.is_emergency_extension_allowed():
                return {
                    'valid': False,
                    'reason': 'Appointment time is outside salon opening hours',
                    'emergency_allowed': SalonHoursService.is_emergency_extension_allowed()
                }
            else:
                return {
                    'valid': True,
                    'warning': 'Appointment extends beyond normal opening hours (emergency extension)',
                    'emergency_extension': True
                }
        
        # Check stylist availability if provided
        if stylist_id:
            work_pattern = WorkPattern.query.filter_by(
                user_id=stylist_id,
                is_active=True
            ).first()
            
            if work_pattern:
                day_name = SalonHoursService.get_day_name(appointment_date)
                if not SalonHoursService._is_stylist_available_at_time(work_pattern, day_name, start_time):
                    return {
                        'valid': False,
                        'reason': 'Stylist is not available at this time'
                    }
        
        return {'valid': True}
    
    @staticmethod
    def get_work_pattern_for_stylist(stylist_id):
        """Get active work pattern for a stylist"""
        return WorkPattern.query.filter_by(
            user_id=stylist_id,
            is_active=True
        ).first()
    
    @staticmethod
    def get_stylist_weekly_hours(stylist_id):
        """Get total weekly hours for a stylist"""
        work_pattern = SalonHoursService.get_work_pattern_for_stylist(stylist_id)
        if not work_pattern:
            return 0
        
        return work_pattern.get_weekly_hours()
    
    @staticmethod
    def calculate_holiday_entitlement(weekly_hours):
        """Calculate holiday entitlement based on weekly hours"""
        # UK standard: 5.6 weeks per year (28 days for full-time)
        # Assuming 40 hours = full-time entitlement
        full_time_hours = 40
        full_time_entitlement = 28  # days
        
        if weekly_hours >= full_time_hours:
            return full_time_entitlement
        elif weekly_hours <= 0:
            return 0
        else:
            # Proportional calculation
            proportion = weekly_hours / full_time_hours
            return round(proportion * full_time_entitlement) 