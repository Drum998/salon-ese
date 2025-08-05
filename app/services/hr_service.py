from datetime import datetime, date
from decimal import Decimal
from app.models import Appointment, AppointmentCost, EmploymentDetails, User, Service, HolidayRequest, HolidayQuota
from app.extensions import db
from sqlalchemy import func, and_


class HRService:
    """HR service for cost calculations and financial tracking"""
    
    @staticmethod
    def calculate_appointment_cost(appointment_id):
        """Calculate cost breakdown for an appointment"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return None
            
        # Get employment details for stylist
        employment = EmploymentDetails.query.filter_by(user_id=appointment.stylist_id).first()
        if not employment:
            return None
            
        # Calculate total service revenue
        total_revenue = 0
        for service_link in appointment.services_link:
            service = service_link.service
            total_revenue += float(service.price)
        
        # Calculate stylist cost based on employment type
        stylist_cost = 0
        calculation_method = ''
        hours_worked = None
        commission_amount = None
        
        if employment.is_employed and employment.hourly_rate:
            # Hourly calculation
            hours = appointment.duration_minutes / 60.0
            stylist_cost = employment.calculate_hourly_cost(hours)
            calculation_method = 'hourly'
            hours_worked = hours
        elif employment.is_self_employed and employment.commission_rate:
            # Commission calculation
            stylist_cost = employment.calculate_commission_cost(total_revenue)
            calculation_method = 'commission'
            commission_amount = stylist_cost
        
        # Calculate salon profit
        salon_profit = total_revenue - stylist_cost
        
        # Create or update appointment cost record
        cost_record = AppointmentCost.query.filter_by(appointment_id=appointment_id).first()
        if not cost_record:
            cost_record = AppointmentCost(
                appointment_id=appointment_id,
                stylist_id=appointment.stylist_id
            )
        
        cost_record.service_revenue = total_revenue
        cost_record.stylist_cost = stylist_cost
        cost_record.salon_profit = salon_profit
        cost_record.calculation_method = calculation_method
        cost_record.hours_worked = hours_worked
        cost_record.commission_amount = commission_amount
        
        db.session.add(cost_record)
        db.session.commit()
        
        return cost_record
    
    @staticmethod
    def calculate_stylist_earnings(stylist_id, start_date=None, end_date=None):
        """Calculate stylist earnings for a date range"""
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()
            
        # Get appointments in date range
        appointments = Appointment.query.filter(
            and_(
                Appointment.stylist_id == stylist_id,
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date,
                Appointment.status == 'completed'
            )
        ).all()
        
        total_earnings = 0
        total_hours = 0
        appointment_count = 0
        
        for appointment in appointments:
            cost_record = AppointmentCost.query.filter_by(appointment_id=appointment.id).first()
            if cost_record:
                total_earnings += float(cost_record.stylist_cost)
                if cost_record.hours_worked:
                    total_hours += float(cost_record.hours_worked)
                appointment_count += 1
        
        return {
            'total_earnings': total_earnings,
            'total_hours': total_hours,
            'appointment_count': appointment_count,
            'average_per_appointment': total_earnings / appointment_count if appointment_count > 0 else 0,
            'hourly_rate_actual': total_earnings / total_hours if total_hours > 0 else 0
        }
    
    @staticmethod
    def calculate_salon_profit(start_date=None, end_date=None):
        """Calculate salon profit for a date range"""
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()
            
        # Get cost records in date range
        cost_records = db.session.query(
            func.sum(AppointmentCost.service_revenue).label('total_revenue'),
            func.sum(AppointmentCost.stylist_cost).label('total_stylist_cost'),
            func.sum(AppointmentCost.salon_profit).label('total_profit'),
            func.count(AppointmentCost.id).label('appointment_count')
        ).join(Appointment).filter(
            and_(
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date,
                Appointment.status == 'completed'
            )
        ).first()
        
        return {
            'total_revenue': float(cost_records.total_revenue or 0),
            'total_stylist_cost': float(cost_records.total_stylist_cost or 0),
            'total_profit': float(cost_records.total_profit or 0),
            'appointment_count': cost_records.appointment_count or 0,
            'profit_margin': (float(cost_records.total_profit or 0) / float(cost_records.total_revenue or 1)) * 100
        }
    
    @staticmethod
    def get_employment_summary():
        """Get summary of all employment details"""
        # Get all stylists with employment details
        stylists = User.query.join(User.roles).filter(
            User.roles.any(name='stylist')
        ).all()
        
        summary = {
            'total_stylists': 0,
            'employed_count': 0,
            'self_employed_count': 0,
            'active_count': 0,
            'inactive_count': 0,
            'total_monthly_cost': 0,
            'employment_details': []
        }
        
        for stylist in stylists:
            employment = EmploymentDetails.query.filter_by(user_id=stylist.id).first()
            if employment:
                summary['total_stylists'] += 1
                
                if employment.is_employed:
                    summary['employed_count'] += 1
                    if employment.base_salary:
                        summary['total_monthly_cost'] += float(employment.base_salary)
                else:
                    summary['self_employed_count'] += 1
                
                if employment.is_currently_employed():
                    summary['active_count'] += 1
                else:
                    summary['inactive_count'] += 1
                
                summary['employment_details'].append({
                    'user_id': stylist.id,
                    'name': f"{stylist.first_name} {stylist.last_name}",
                    'employment_type': employment.employment_type,
                    'start_date': employment.start_date,
                    'end_date': employment.end_date,
                    'is_active': employment.is_currently_employed(),
                    'rate': employment.get_current_rate(),
                    'job_role': employment.job_role
                })
        
        return summary
    
    @staticmethod
    def get_stylist_performance_report(stylist_id, start_date=None, end_date=None):
        """Get detailed performance report for a stylist"""
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()
            
        stylist = User.query.get(stylist_id)
        employment = EmploymentDetails.query.filter_by(user_id=stylist_id).first()
        
        if not stylist or not employment:
            return None
            
        # Get appointments and costs
        appointments = Appointment.query.filter(
            and_(
                Appointment.stylist_id == stylist_id,
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date
            )
        ).all()
        
        total_appointments = len(appointments)
        completed_appointments = len([a for a in appointments if a.status == 'completed'])
        cancelled_appointments = len([a for a in appointments if a.status == 'cancelled'])
        
        # Calculate earnings
        earnings_data = HRService.calculate_stylist_earnings(stylist_id, start_date, end_date)
        
        return {
            'stylist_name': f"{stylist.first_name} {stylist.last_name}",
            'employment_type': employment.employment_type,
            'job_role': employment.job_role,
            'start_date': employment.start_date,
            'is_currently_employed': employment.is_currently_employed(),
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'completion_rate': (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0,
            'earnings': earnings_data
        }
    
    @staticmethod
    def get_holiday_summary():
        """Get holiday summary for all staff"""
        from app.services.holiday_service import HolidayService
        
        # Get all stylists
        stylists = User.query.join(User.roles).filter(
            User.roles.any(name='stylist')
        ).all()
        
        summary = {
            'total_stylists': len(stylists),
            'pending_requests': 0,
            'approved_requests': 0,
            'rejected_requests': 0,
            'total_entitlement': 0,
            'total_taken': 0,
            'total_remaining': 0,
            'stylist_holidays': []
        }
        
        # Get pending requests count
        pending_requests = HolidayRequest.query.filter_by(status='pending').count()
        summary['pending_requests'] = pending_requests
        
        for stylist in stylists:
            holiday_data = HolidayService.get_holiday_summary(stylist.id)
            if holiday_data and holiday_data['quota']:
                quota = holiday_data['quota']
                summary['total_entitlement'] += quota.holiday_days_entitled
                summary['total_taken'] += quota.holiday_days_taken
                summary['total_remaining'] += quota.holiday_days_remaining
                
                summary['stylist_holidays'].append({
                    'user_id': stylist.id,
                    'name': f"{stylist.first_name} {stylist.last_name}",
                    'entitled': quota.holiday_days_entitled,
                    'taken': quota.holiday_days_taken,
                    'remaining': quota.holiday_days_remaining,
                    'pending_requests': len(holiday_data['pending_requests']),
                    'approved_requests': len(holiday_data['approved_requests']),
                    'rejected_requests': len(holiday_data['rejected_requests'])
                })
        
        return summary 