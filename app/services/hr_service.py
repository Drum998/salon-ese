from datetime import datetime, date
from decimal import Decimal
from app.models import Appointment, AppointmentCost, EmploymentDetails, User, Service, HolidayRequest, HolidayQuota, BillingElement
from app.extensions import db
from sqlalchemy import func, and_
import json


class HRService:
    """HR service for cost calculations and financial tracking"""
    
    @staticmethod
    def calculate_appointment_cost(appointment_id):
        """Calculate cost breakdown for an appointment with enhanced commission system"""
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
        commission_breakdown = None
        billing_elements_applied = None
        billing_method = employment.billing_method
        
        if employment.is_employed and employment.hourly_rate:
            # Hourly calculation
            hours = appointment.duration_minutes / 60.0
            stylist_cost = employment.calculate_hourly_cost(hours)
            calculation_method = 'hourly'
            hours_worked = hours
        elif employment.is_self_employed and employment.commission_rate:
            # Enhanced commission calculation with billing elements
            commission_data = HRService.calculate_commission_with_billing_elements(appointment_id)
            if commission_data:
                stylist_cost = commission_data['total_commission']
                calculation_method = 'commission'
                commission_amount = stylist_cost
                commission_breakdown = commission_data['commission_breakdown']
                billing_elements_applied = commission_data['billing_elements_applied']
                billing_method = commission_data['billing_method']
        
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
        cost_record.commission_breakdown = commission_breakdown
        cost_record.billing_elements_applied = billing_elements_applied
        cost_record.billing_method = billing_method
        
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
    def calculate_commission_breakdown(appointment_id):
        """Calculate detailed commission breakdown including billing elements"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return None
            
        # Get employment details for stylist
        employment = EmploymentDetails.query.filter_by(user_id=appointment.stylist_id).first()
        if not employment or not employment.is_self_employed:
            return None
            
        # Calculate total service revenue
        total_revenue = 0
        for service_link in appointment.services_link:
            service = service_link.service
            total_revenue += float(service.price)
        
        # Get billing elements
        billing_elements = BillingElement.get_active_elements()
        
        # Calculate commission breakdown
        commission_percentage = float(employment.commission_rate) if employment.commission_rate else 0
        total_commission = total_revenue * (commission_percentage / 100)
        
        # Calculate billing elements breakdown
        elements_breakdown = {}
        for element in billing_elements:
            element_amount = total_revenue * (float(element.percentage) / 100)
            elements_breakdown[element.name] = {
                'percentage': float(element.percentage),
                'amount': element_amount,
                'commission_portion': element_amount * (commission_percentage / 100)
            }
        
        breakdown = {
            'total_commission': total_commission,
            'commission_percentage': commission_percentage,
            'service_revenue': total_revenue,
            'calculation_method': 'percentage',
            'billing_method': employment.billing_method,
            'billing_elements': elements_breakdown,
            'stylist_earnings': total_commission,
            'salon_portion': total_revenue - total_commission
        }
        
        return breakdown
    
    @staticmethod
    def calculate_stylist_commission_performance(stylist_id, start_date=None, end_date=None):
        """Calculate stylist commission performance metrics"""
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
        
        total_commission = 0
        total_revenue = 0
        appointment_count = 0
        commission_appointments = 0
        
        for appointment in appointments:
            cost_record = AppointmentCost.query.filter_by(appointment_id=appointment.id).first()
            if cost_record and cost_record.calculation_method == 'commission':
                total_commission += float(cost_record.commission_amount or 0)
                total_revenue += float(cost_record.service_revenue)
                commission_appointments += 1
            appointment_count += 1
        
        # Calculate performance metrics
        avg_commission_per_appointment = total_commission / commission_appointments if commission_appointments > 0 else 0
        commission_efficiency = (total_commission / total_revenue * 100) if total_revenue > 0 else 0
        commission_rate = (commission_appointments / appointment_count * 100) if appointment_count > 0 else 0
        
        return {
            'total_commission': total_commission,
            'total_revenue': total_revenue,
            'appointment_count': appointment_count,
            'commission_appointments': commission_appointments,
            'avg_commission_per_appointment': avg_commission_per_appointment,
            'commission_efficiency': commission_efficiency,
            'commission_rate': commission_rate,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    @staticmethod
    def calculate_salon_commission_summary(start_date=None, end_date=None):
        """Calculate salon-wide commission summary and analytics"""
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()
            
        # Get all commission-based cost records in date range
        cost_records = db.session.query(
            func.sum(AppointmentCost.service_revenue).label('total_revenue'),
            func.sum(AppointmentCost.commission_amount).label('total_commission'),
            func.sum(AppointmentCost.salon_profit).label('total_salon_profit'),
            func.count(AppointmentCost.id).label('appointment_count'),
            func.avg(AppointmentCost.commission_amount).label('avg_commission')
        ).join(Appointment).filter(
            and_(
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date,
                Appointment.status == 'completed',
                AppointmentCost.calculation_method == 'commission'
            )
        ).first()
        
        # Get stylist breakdown
        stylist_breakdown = db.session.query(
            AppointmentCost.stylist_id,
            func.sum(AppointmentCost.service_revenue).label('stylist_revenue'),
            func.sum(AppointmentCost.commission_amount).label('stylist_commission'),
            func.count(AppointmentCost.id).label('appointment_count')
        ).join(Appointment).filter(
            and_(
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date,
                Appointment.status == 'completed',
                AppointmentCost.calculation_method == 'commission'
            )
        ).group_by(AppointmentCost.stylist_id).all()
        
        # Calculate summary metrics
        total_revenue = float(cost_records.total_revenue or 0)
        total_commission = float(cost_records.total_commission or 0)
        total_salon_profit = float(cost_records.total_salon_profit or 0)
        appointment_count = cost_records.appointment_count or 0
        avg_commission = float(cost_records.avg_commission or 0)
        
        commission_efficiency = (total_commission / total_revenue * 100) if total_revenue > 0 else 0
        profit_margin = (total_salon_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'total_commission': total_commission,
            'total_salon_profit': total_salon_profit,
            'appointment_count': appointment_count,
            'avg_commission': avg_commission,
            'commission_efficiency': commission_efficiency,
            'profit_margin': profit_margin,
            'stylist_breakdown': [
                {
                    'stylist_id': record.stylist_id,
                    'stylist_name': User.query.get(record.stylist_id).first_name + ' ' + User.query.get(record.stylist_id).last_name,
                    'revenue': float(record.stylist_revenue),
                    'commission': float(record.stylist_commission),
                    'appointment_count': record.appointment_count,
                    'commission_efficiency': (float(record.stylist_commission) / float(record.stylist_revenue) * 100) if record.stylist_revenue > 0 else 0
                }
                for record in stylist_breakdown
            ],
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
    
    @staticmethod
    def calculate_commission_with_billing_elements(appointment_id):
        """Calculate commission including billing elements breakdown"""
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return None
            
        # Get employment details
        employment = EmploymentDetails.query.filter_by(user_id=appointment.stylist_id).first()
        if not employment or not employment.is_self_employed:
            return None
            
        # Calculate total service revenue
        total_revenue = 0
        for service_link in appointment.services_link:
            service = service_link.service
            total_revenue += float(service.price)
        
        # Get billing elements
        billing_elements = BillingElement.get_active_elements()
        
        # Calculate commission
        commission_percentage = float(employment.commission_rate) if employment.commission_rate else 0
        total_commission = total_revenue * (commission_percentage / 100)
        
        # Calculate billing elements breakdown
        elements_applied = {}
        for element in billing_elements:
            element_amount = total_revenue * (float(element.percentage) / 100)
            elements_applied[element.name] = {
                'percentage': float(element.percentage),
                'amount': element_amount,
                'commission_portion': element_amount * (commission_percentage / 100)
            }
        
        # Create commission breakdown
        commission_breakdown = {
            'total_commission': total_commission,
            'commission_percentage': commission_percentage,
            'service_revenue': total_revenue,
            'calculation_method': 'percentage',
            'billing_method': employment.billing_method,
            'stylist_earnings': total_commission,
            'salon_portion': total_revenue - total_commission
        }
        
        return {
            'commission_breakdown': commission_breakdown,
            'billing_elements_applied': elements_applied,
            'billing_method': employment.billing_method,
            'total_commission': total_commission,
            'total_revenue': total_revenue
        }
    
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