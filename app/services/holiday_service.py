from datetime import datetime, date, timedelta
from decimal import Decimal
from app.models import HolidayRequest, HolidayQuota, WorkPattern, EmploymentDetails, User, Appointment
from app.extensions import db
from sqlalchemy import func, and_, or_


class HolidayService:
    """Holiday service for quota calculations, request validation, and approval workflow"""
    
    @staticmethod
    def calculate_holiday_entitlement(user_id, year=None):
        """Calculate holiday entitlement for a user based on their work pattern and employment type"""
        if year is None:
            year = date.today().year
            
        # Get user's work pattern
        work_pattern = WorkPattern.query.filter_by(
            user_id=user_id, 
            is_active=True
        ).first()
        
        if not work_pattern:
            return None
            
        # Get employment details
        employment = EmploymentDetails.query.filter_by(user_id=user_id).first()
        if not employment:
            return None
            
        # Calculate weekly hours from work pattern
        weekly_hours = work_pattern.get_weekly_hours()
        
        # Calculate entitlement based on UK statutory requirements
        # Full-time (37.5+ hours): 28 days
        # Part-time: Pro-rated based on hours
        if weekly_hours >= 37.5:
            entitlement_days = 28
        else:
            # Pro-rate based on hours (28 days for 37.5 hours)
            entitlement_days = (weekly_hours / 37.5) * 28
            
        # Round to nearest half day
        entitlement_days = round(entitlement_days * 2) / 2
        
        return {
            'weekly_hours': weekly_hours,
            'entitlement_days': entitlement_days,
            'employment_type': employment.employment_type
        }
    
    @staticmethod
    def get_or_create_holiday_quota(user_id, year=None):
        """Get existing quota or create new one for the year"""
        if year is None:
            year = date.today().year
            
        quota = HolidayQuota.query.filter_by(user_id=user_id, year=year).first()
        
        if not quota:
            # Calculate entitlement
            entitlement_data = HolidayService.calculate_holiday_entitlement(user_id, year)
            if not entitlement_data:
                return None
                
            quota = HolidayQuota(
                user_id=user_id,
                year=year,
                total_hours_per_week=entitlement_data['weekly_hours'],
                holiday_days_entitled=entitlement_data['entitlement_days'],
                holiday_days_taken=0,
                holiday_days_remaining=entitlement_data['entitlement_days']
            )
            db.session.add(quota)
            db.session.commit()
        
        return quota
    
    @staticmethod
    def validate_holiday_request(user_id, start_date, end_date, notes=None):
        """Validate a holiday request against quotas, work patterns, and conflicts"""
        errors = []
        warnings = []
        
        # Basic date validation
        if start_date > end_date:
            errors.append("Start date must be before end date")
            
        if start_date < date.today():
            errors.append("Cannot request holidays in the past")
            
        # Calculate requested days (excluding weekends)
        requested_days = HolidayService._calculate_working_days(start_date, end_date)
        if requested_days <= 0:
            errors.append("No working days in the selected date range")
            
        # Check quota availability
        year = start_date.year
        quota = HolidayService.get_or_create_holiday_quota(user_id, year)
        if not quota:
            errors.append("Unable to calculate holiday entitlement")
        elif quota.holiday_days_remaining < requested_days:
            errors.append(f"Insufficient holiday days. Available: {quota.holiday_days_remaining}, Requested: {requested_days}")
            
        # Check for overlapping requests
        overlapping_requests = HolidayRequest.query.filter(
            and_(
                HolidayRequest.user_id == user_id,
                HolidayRequest.status.in_(['pending', 'approved']),
                or_(
                    and_(HolidayRequest.start_date <= start_date, HolidayRequest.end_date >= start_date),
                    and_(HolidayRequest.start_date <= end_date, HolidayRequest.end_date >= end_date),
                    and_(HolidayRequest.start_date >= start_date, HolidayRequest.end_date <= end_date)
                )
            )
        ).all()
        
        if overlapping_requests:
            errors.append("You have overlapping holiday requests for this period")
            
        # Check work pattern conflicts
        work_pattern = WorkPattern.query.filter_by(user_id=user_id, is_active=True).first()
        if work_pattern:
            # Check if requested dates fall on working days
            working_days = work_pattern.work_schedule.get('working_days', [])
            requested_weekdays = []
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() in working_days:
                    requested_weekdays.append(current_date)
                current_date += timedelta(days=1)
                
            if not requested_weekdays:
                warnings.append("Selected dates do not fall on your working days")
                
        # Check for appointment conflicts (future enhancement)
        # This could check for existing appointments in the date range
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'requested_days': requested_days,
            'quota': quota
        }
    
    @staticmethod
    def create_holiday_request(user_id, start_date, end_date, notes=None):
        """Create a new holiday request"""
        # Validate the request
        validation = HolidayService.validate_holiday_request(user_id, start_date, end_date, notes)
        
        if not validation['valid']:
            return None, validation['errors']
            
        # Create the request
        request = HolidayRequest(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            days_requested=validation['requested_days'],
            notes=notes,
            status='pending'
        )
        
        db.session.add(request)
        db.session.commit()
        
        return request, []
    
    @staticmethod
    def approve_holiday_request(request_id, approved_by_user_id, notes=None):
        """Approve a holiday request and update quota"""
        request = HolidayRequest.query.get(request_id)
        if not request:
            return False, "Request not found"
            
        if request.status != 'pending':
            return False, "Request is not pending"
            
        # Update request status
        request.status = 'approved'
        request.approved_by_id = approved_by_user_id
        request.approved_at = datetime.now()
        if notes:
            request.notes = f"{request.notes or ''}\n\nApproval notes: {notes}"
            
        # Update quota
        year = request.start_date.year
        quota = HolidayService.get_or_create_holiday_quota(request.user_id, year)
        if quota:
            quota.holiday_days_taken += request.days_requested
            quota.holiday_days_remaining = quota.holiday_days_entitled - quota.holiday_days_taken
            quota.update_remaining_days()
            
        db.session.commit()
        
        return True, "Request approved successfully"
    
    @staticmethod
    def reject_holiday_request(request_id, rejected_by_user_id, notes=None):
        """Reject a holiday request"""
        request = HolidayRequest.query.get(request_id)
        if not request:
            return False, "Request not found"
            
        if request.status != 'pending':
            return False, "Request is not pending"
            
        # Update request status
        request.status = 'rejected'
        request.approved_by_id = rejected_by_user_id  # Using same field for consistency
        request.approved_at = datetime.now()
        if notes:
            request.notes = f"{request.notes or ''}\n\nRejection notes: {notes}"
            
        db.session.commit()
        
        return True, "Request rejected successfully"
    
    @staticmethod
    def get_user_holiday_requests(user_id, status=None):
        """Get holiday requests for a user"""
        query = HolidayRequest.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
            
        return query.order_by(HolidayRequest.created_at.desc()).all()
    
    @staticmethod
    def get_pending_holiday_requests():
        """Get all pending holiday requests for admin approval"""
        return HolidayRequest.query.filter_by(status='pending').order_by(HolidayRequest.created_at.asc()).all()
    
    @staticmethod
    def get_holiday_summary(user_id, year=None):
        """Get holiday summary for a user"""
        if year is None:
            year = date.today().year
            
        quota = HolidayService.get_or_create_holiday_quota(user_id, year)
        if not quota:
            return None
            
        # Get requests for the year
        requests = HolidayRequest.query.filter(
            and_(
                HolidayRequest.user_id == user_id,
                func.extract('year', HolidayRequest.start_date) == year
            )
        ).all()
        
        return {
            'quota': quota,
            'requests': requests,
            'approved_requests': [r for r in requests if r.status == 'approved'],
            'pending_requests': [r for r in requests if r.status == 'pending'],
            'rejected_requests': [r for r in requests if r.status == 'rejected']
        }
    
    @staticmethod
    def _calculate_working_days(start_date, end_date):
        """Calculate working days between two dates (excluding weekends)"""
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Monday = 0, Sunday = 6
            if current_date.weekday() < 5:  # Monday to Friday
                working_days += 1
            current_date += timedelta(days=1)
            
        return working_days 