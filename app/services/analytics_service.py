#!/usr/bin/env python3
"""
Analytics Service for Advanced Reporting Features
Provides comprehensive analytics for holiday, commission, and staff utilization
"""

from app import db
from app.models import (
    User, Role, Appointment, AppointmentCost, EmploymentDetails,
    HolidayRequest, HolidayQuota, WorkPattern, Service, BillingElement
)
from app.services.hr_service import HRService
from app.services.holiday_service import HolidayService
from decimal import Decimal
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_, case
import json


class AnalyticsService:
    """Comprehensive analytics service for advanced reporting features"""

    @staticmethod
    def get_executive_dashboard_data(start_date=None, end_date=None):
        """Get high-level KPIs for executive dashboard"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        # Revenue and commission metrics
        revenue_data = HRService.calculate_salon_commission_summary(start_date, end_date)
        
        # Staff metrics
        total_stylists = User.query.join(User.roles).filter(Role.name == 'stylist').count()
        active_stylists = Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).with_entities(Appointment.stylist_id).distinct().count()

        # Holiday metrics
        holiday_requests = HolidayRequest.query.filter(
            HolidayRequest.start_date >= start_date,
            HolidayRequest.start_date <= end_date
        ).count()
        
        approved_holidays = HolidayRequest.query.filter(
            HolidayRequest.start_date >= start_date,
            HolidayRequest.start_date <= end_date,
            HolidayRequest.status == 'approved'
        ).count()

        # Appointment metrics
        total_appointments = Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).count()

        return {
            'revenue': revenue_data.get('total_revenue', 0),
            'commission': revenue_data.get('total_commission', 0),
            'commission_efficiency': revenue_data.get('commission_efficiency', 0),
            'total_stylists': total_stylists,
            'active_stylists': active_stylists,
            'staff_utilization': (active_stylists / total_stylists * 100) if total_stylists > 0 else 0,
            'holiday_requests': holiday_requests,
            'approved_holidays': approved_holidays,
            'holiday_approval_rate': (approved_holidays / holiday_requests * 100) if holiday_requests > 0 else 0,
            'total_appointments': total_appointments,
            'avg_appointments_per_day': total_appointments / max((end_date - start_date).days, 1),
            'period_start': start_date,
            'period_end': end_date
        }

    @staticmethod
    def analyze_holiday_trends(start_date=None, end_date=None):
        """Analyze holiday request patterns and trends"""
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()

        # Monthly holiday request trends
        monthly_trends = db.session.query(
            func.date_trunc('month', HolidayRequest.start_date).label('month'),
            func.count(HolidayRequest.id).label('total_requests'),
            func.count(case([(HolidayRequest.status == 'approved', 1)])).label('approved'),
            func.count(case([(HolidayRequest.status == 'rejected', 1)])).label('rejected'),
            func.count(case([(HolidayRequest.status == 'pending', 1)])).label('pending')
        ).filter(
            HolidayRequest.start_date >= start_date,
            HolidayRequest.start_date <= end_date
        ).group_by(
            func.date_trunc('month', HolidayRequest.start_date)
        ).order_by('month').all()

        # Staff holiday utilization
        staff_utilization = db.session.query(
            User.username,
            func.count(HolidayRequest.id).label('total_requests'),
            func.count(case([(HolidayRequest.status == 'approved', 1)])).label('approved_requests'),
            func.avg(HolidayRequest.duration_days).label('avg_duration')
        ).join(
            HolidayRequest, User.id == HolidayRequest.user_id
        ).filter(
            HolidayRequest.start_date >= start_date,
            HolidayRequest.start_date <= end_date
        ).group_by(User.id, User.username).all()

        # Holiday conflict analysis
        conflicts = AnalyticsService._detect_holiday_conflicts(start_date, end_date)

        return {
            'monthly_trends': [
                {
                    'month': trend.month.strftime('%Y-%m'),
                    'total_requests': trend.total_requests,
                    'approved': trend.approved,
                    'rejected': trend.rejected,
                    'pending': trend.pending,
                    'approval_rate': (trend.approved / trend.total_requests * 100) if trend.total_requests > 0 else 0
                }
                for trend in monthly_trends
            ],
            'staff_utilization': [
                {
                    'username': util.username,
                    'total_requests': util.total_requests,
                    'approved_requests': util.approved_requests,
                    'avg_duration': float(util.avg_duration) if util.avg_duration else 0,
                    'approval_rate': (util.approved_requests / util.total_requests * 100) if util.total_requests > 0 else 0
                }
                for util in staff_utilization
            ],
            'conflicts': conflicts
        }

    @staticmethod
    def _detect_holiday_conflicts(start_date, end_date):
        """Detect potential holiday scheduling conflicts"""
        conflicts = []
        
        # Find overlapping holiday requests
        overlapping_requests = db.session.query(
            HolidayRequest.id,
            HolidayRequest.user_id,
            HolidayRequest.start_date,
            HolidayRequest.end_date,
            User.username
        ).join(User).filter(
            HolidayRequest.start_date <= end_date,
            HolidayRequest.end_date >= start_date,
            HolidayRequest.status == 'approved'
        ).all()

        # Check for multiple staff on holiday simultaneously
        for request in overlapping_requests:
            overlapping_count = HolidayRequest.query.filter(
                HolidayRequest.status == 'approved',
                HolidayRequest.start_date <= request.end_date,
                HolidayRequest.end_date >= request.start_date
            ).count()
            
            if overlapping_count > 2:  # More than 2 staff on holiday at same time
                conflicts.append({
                    'type': 'multiple_staff_holiday',
                    'date_range': f"{request.start_date} to {request.end_date}",
                    'affected_staff': overlapping_count,
                    'description': f"{overlapping_count} staff members on holiday simultaneously"
                })

        return conflicts

    @staticmethod
    def analyze_commission_trends(start_date=None, end_date=None):
        """Analyze commission performance trends"""
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()

        # Monthly commission trends
        monthly_commission = db.session.query(
            func.date_trunc('month', Appointment.appointment_date).label('month'),
            func.sum(AppointmentCost.service_revenue).label('total_revenue'),
            func.sum(AppointmentCost.commission_amount).label('total_commission'),
            func.avg(AppointmentCost.commission_amount).label('avg_commission')
        ).join(
            AppointmentCost, Appointment.id == AppointmentCost.appointment_id
        ).filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date,
            AppointmentCost.commission_amount > 0
        ).group_by(
            func.date_trunc('month', Appointment.appointment_date)
        ).order_by('month').all()

        # Stylist performance rankings
        stylist_rankings = db.session.query(
            User.username,
            func.sum(AppointmentCost.service_revenue).label('total_revenue'),
            func.sum(AppointmentCost.commission_amount).label('total_commission'),
            func.avg(AppointmentCost.commission_amount).label('avg_commission'),
            func.count(Appointment.id).label('appointment_count')
        ).join(
            Appointment, User.id == Appointment.stylist_id
        ).join(
            AppointmentCost, Appointment.id == AppointmentCost.appointment_id
        ).filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date,
            AppointmentCost.commission_amount > 0
        ).group_by(User.id, User.username).order_by(
            func.sum(AppointmentCost.commission_amount).desc()
        ).all()

        # Billing element performance
        billing_elements = BillingElement.get_active_elements()
        element_performance = {}
        
        for element in billing_elements:
            # This would require more complex querying based on billing_elements_applied JSON
            # For now, we'll provide a placeholder structure
            element_performance[element.name] = {
                'percentage': float(element.percentage),
                'total_revenue': 0,  # Would need to calculate from JSON data
                'commission_generated': 0  # Would need to calculate from JSON data
            }

        return {
            'monthly_trends': [
                {
                    'month': trend.month.strftime('%Y-%m'),
                    'total_revenue': float(trend.total_revenue) if trend.total_revenue else 0,
                    'total_commission': float(trend.total_commission) if trend.total_commission else 0,
                    'avg_commission': float(trend.avg_commission) if trend.avg_commission else 0,
                    'commission_rate': (float(trend.total_commission) / float(trend.total_revenue) * 100) if trend.total_revenue else 0
                }
                for trend in monthly_commission
            ],
            'stylist_rankings': [
                {
                    'username': ranking.username,
                    'total_revenue': float(ranking.total_revenue) if ranking.total_revenue else 0,
                    'total_commission': float(ranking.total_commission) if ranking.total_commission else 0,
                    'avg_commission': float(ranking.avg_commission) if ranking.avg_commission else 0,
                    'appointment_count': ranking.appointment_count,
                    'commission_efficiency': (float(ranking.total_commission) / float(ranking.total_revenue) * 100) if ranking.total_revenue else 0
                }
                for ranking in stylist_rankings
            ],
            'billing_elements': element_performance
        }

    @staticmethod
    def calculate_staff_utilization(start_date=None, end_date=None):
        """Calculate comprehensive staff utilization metrics"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        # Get all stylists
        stylists = User.query.join(User.roles).filter(Role.name == 'stylist').all()
        
        utilization_data = []
        
        for stylist in stylists:
            # Get work pattern
            work_pattern = WorkPattern.query.filter_by(user_id=stylist.id).first()
            
            # Get appointments in date range
            appointments = Appointment.query.filter(
                Appointment.stylist_id == stylist.id,
                Appointment.appointment_date >= start_date,
                Appointment.appointment_date <= end_date
            ).all()
            
            # Calculate scheduled hours
            scheduled_hours = 0
            if work_pattern:
                # Calculate total scheduled hours based on work pattern
                # This is a simplified calculation - would need more complex logic
                scheduled_hours = 40  # Placeholder
            
            # Calculate actual hours (from appointments)
            actual_hours = sum(appointment.duration for appointment in appointments)
            
            # Calculate utilization rate
            utilization_rate = (actual_hours / scheduled_hours * 100) if scheduled_hours > 0 else 0
            
            # Calculate revenue per hour
            total_revenue = sum(
                AppointmentCost.query.filter_by(appointment_id=appointment.id).first().service_revenue
                for appointment in appointments
                if AppointmentCost.query.filter_by(appointment_id=appointment.id).first()
            )
            
            revenue_per_hour = (total_revenue / actual_hours) if actual_hours > 0 else 0
            
            utilization_data.append({
                'username': stylist.username,
                'scheduled_hours': scheduled_hours,
                'actual_hours': actual_hours,
                'utilization_rate': utilization_rate,
                'appointment_count': len(appointments),
                'total_revenue': float(total_revenue),
                'revenue_per_hour': float(revenue_per_hour),
                'avg_appointment_duration': (actual_hours / len(appointments)) if appointments else 0
            })
        
        return {
            'staff_utilization': utilization_data,
            'avg_utilization_rate': sum(data['utilization_rate'] for data in utilization_data) / len(utilization_data) if utilization_data else 0,
            'total_scheduled_hours': sum(data['scheduled_hours'] for data in utilization_data),
            'total_actual_hours': sum(data['actual_hours'] for data in utilization_data),
            'total_revenue': sum(data['total_revenue'] for data in utilization_data)
        }

    @staticmethod
    def generate_capacity_recommendations():
        """Generate capacity planning recommendations"""
        # Analyze current capacity vs demand
        current_appointments = Appointment.query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.appointment_date <= date.today() + timedelta(days=30)
        ).all()
        
        # Group by date and stylist
        daily_capacity = {}
        for appointment in current_appointments:
            date_key = appointment.appointment_date.strftime('%Y-%m-%d')
            if date_key not in daily_capacity:
                daily_capacity[date_key] = {}
            
            stylist_id = appointment.stylist_id
            if stylist_id not in daily_capacity[date_key]:
                daily_capacity[date_key][stylist_id] = 0
            
            daily_capacity[date_key][stylist_id] += appointment.duration
        
        recommendations = []
        
        for date_key, stylist_data in daily_capacity.items():
            total_hours = sum(stylist_data.values())
            stylist_count = len(stylist_data)
            
            # Simple capacity analysis
            if total_hours > 40:  # Over capacity
                recommendations.append({
                    'date': date_key,
                    'type': 'over_capacity',
                    'description': f"High demand day - {total_hours} hours scheduled",
                    'suggestion': 'Consider adding temporary staff or extending hours'
                })
            elif total_hours < 20:  # Under capacity
                recommendations.append({
                    'date': date_key,
                    'type': 'under_capacity',
                    'description': f"Low demand day - {total_hours} hours scheduled",
                    'suggestion': 'Consider promotional activities or staff training'
                })
        
        return {
            'recommendations': recommendations,
            'capacity_analysis': {
                'total_days_analyzed': len(daily_capacity),
                'over_capacity_days': len([r for r in recommendations if r['type'] == 'over_capacity']),
                'under_capacity_days': len([r for r in recommendations if r['type'] == 'under_capacity'])
            }
        } 