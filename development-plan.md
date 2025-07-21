# Salon ESE Development Plan
## Enhanced Client Requirements Integration

This document outlines the comprehensive plan for integrating the new client requirements from `new_requirements.txt` into the existing salon booking system, while maintaining and enhancing all existing functionality.

---

## 📋 New Requirements Analysis

Based on the new requirements document, the following major enhancements need to be implemented:

### **Core New Requirements:**
1. **Enhanced Appointment Booking System**
   - Multiple services per appointment
   - Service waiting times (color processing)
   - Stylist-specific vs standard timing
   - Emergency hour extension for appointments

2. **Customer Management System**
   - Backend customer addition (management/stylist only)
   - Customer service history tracking
   - Previous service booking suggestions

3. **Stylist View Enhancements**
   - Global salon view vs personal view toggle
   - Cross-stylist booking capabilities
   - Real-time availability checking

4. **Service Management Enhancements**
   - Service waiting times
   - Service combinations
   - Standard vs stylist-specific timing

5. **Holiday Management System**
   - Holiday impact reporting
   - Booking value analysis
   - Staff availability tracking

6. **UI/UX Improvements**
   - Fluid design changes
   - Task completion from current page
   - Fix broken functionality

---

## 🎯 Implementation Plan

### **Phase 1: Database Schema Extensions & Core Models**

#### **Task 1.1: Enhanced Service Management**
**New Models Required:**

1. **ServiceWaitingTime Model**
   ```python
   class ServiceWaitingTime(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
       waiting_time_minutes = db.Column(db.Integer, nullable=False, default=0)
       is_active = db.Column(db.Boolean, default=True)
       created_at = db.Column(db.DateTime, default=uk_utcnow)
       
       # Relationships
       service = db.relationship('Service', backref='waiting_times')
   ```

2. **StylistServiceTiming Model**
   ```python
   class StylistServiceTiming(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
       service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
       custom_duration_minutes = db.Column(db.Integer, nullable=False)
       is_active = db.Column(db.Boolean, default=True)
       created_at = db.Column(db.DateTime, default=uk_utcnow)
       
       # Relationships
       stylist = db.relationship('User', backref='service_timings')
       service = db.relationship('Service', backref='stylist_timings')
   ```

#### **Task 1.2: Enhanced Appointment System**
**Updates to Existing Models:**

1. **Appointment Model Extensions**
   ```python
   # Add to existing Appointment model:
   services = db.relationship('AppointmentService', backref='appointment', cascade='all, delete-orphan')
   emergency_extension = db.Column(db.Boolean, default=False)
   salon_extension_time = db.Column(db.Time)  # Time salon was extended to
   ```

2. **AppointmentService Model (New)**
   ```python
   class AppointmentService(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
       service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
       sequence_order = db.Column(db.Integer, nullable=False)  # Order of services
       start_time = db.Column(db.Time, nullable=False)
       end_time = db.Column(db.Time, nullable=False)
       waiting_time_minutes = db.Column(db.Integer, default=0)
       stylist_duration_used = db.Column(db.Boolean, default=False)  # True if stylist timing used
       created_at = db.Column(db.DateTime, default=uk_utcnow)
       
       # Relationships
       service = db.relationship('Service', backref='appointment_services')
   ```

#### **Task 1.3: Customer Management System**
**New Models Required:**

1. **CustomerServiceHistory Model**
   ```python
   class CustomerServiceHistory(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
       service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
       appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
       service_date = db.Column(db.Date, nullable=False)
       stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
       actual_duration_minutes = db.Column(db.Integer)
       notes = db.Column(db.Text)
       created_at = db.Column(db.DateTime, default=uk_utcnow)
       
       # Relationships
       customer = db.relationship('User', foreign_keys=[customer_id], backref='service_history')
       service = db.relationship('Service', backref='customer_history')
       appointment = db.relationship('Appointment', backref='service_history')
       stylist = db.relationship('User', foreign_keys=[stylist_id], backref='provided_services')
   ```

2. **CustomerPreferences Model**
   ```python
   class CustomerPreferences(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
       preferred_services = db.Column(db.JSON)  # List of preferred service IDs
       preferred_stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       booking_preferences = db.Column(db.JSON)  # Booking preferences
       created_at = db.Column(db.DateTime, default=uk_utcnow)
       updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
       
       # Relationships
       customer = db.relationship('User', foreign_keys=[customer_id], backref='preferences')
       preferred_stylist = db.relationship('User', foreign_keys=[preferred_stylist_id], backref='preferred_by')
   ```

#### **Task 1.4: Enhanced Holiday Management**
**Updates to Existing Models:**

1. **HolidayRequest Model Extensions**
   ```python
   # Add to existing HolidayRequest model:
   booking_impact_value = db.Column(db.Numeric(10, 2))  # Potential lost revenue
   affected_appointments = db.Column(db.Integer, default=0)
   other_staff_off = db.Column(db.JSON)  # List of other staff off during period
   ```

2. **HolidayImpactReport Model (New)**
   ```python
   class HolidayImpactReport(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       holiday_request_id = db.Column(db.Integer, db.ForeignKey('holiday_request.id'), nullable=False)
       report_date = db.Column(db.Date, nullable=False)
       potential_bookings_lost = db.Column(db.Integer, default=0)
       potential_revenue_lost = db.Column(db.Numeric(10, 2), default=0)
       staff_availability = db.Column(db.JSON)  # Staff availability during period
       created_at = db.Column(db.DateTime, default=uk_utcnow)
       
       # Relationships
       holiday_request = db.relationship('HolidayRequest', backref='impact_reports')
   ```

### **Phase 2: Enhanced Appointment Booking System**

#### **Task 2.1: Multiple Service Booking**
**New Routes Required:**
- `/appointments/book-multi-service` - Multi-service booking interface
- `/appointments/calculate-timing` - AJAX endpoint for timing calculations
- `/appointments/check-availability` - Enhanced availability checking

**New Forms Required:**
```python
class MultiServiceBookingForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    stylist_id = SelectField('Stylist', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Date', validators=[DataRequired()])
    start_time = SelectField('Start Time', validators=[DataRequired()])
    services = SelectMultipleField('Services', coerce=int, validators=[DataRequired()])
    use_stylist_timing = BooleanField('Use Stylist Timing', default=False)
    emergency_extension = BooleanField('Allow Emergency Extension', default=False)
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Book Appointment')
```

#### **Task 2.2: Service Timing System**
**Business Logic Implementation:**
```python
def calculate_appointment_timing(services, stylist_id, use_stylist_timing=False):
    """
    Calculate total appointment timing including waiting times
    """
    total_duration = 0
    service_sequence = []
    
    for service in services:
        # Get stylist-specific timing if requested
        if use_stylist_timing:
            stylist_timing = StylistServiceTiming.query.filter_by(
                stylist_id=stylist_id, 
                service_id=service.id,
                is_active=True
            ).first()
            service_duration = stylist_timing.custom_duration_minutes if stylist_timing else service.duration
        else:
            service_duration = service.duration
        
        # Add waiting time if applicable
        waiting_time = ServiceWaitingTime.query.filter_by(
            service_id=service.id,
            is_active=True
        ).first()
        
        total_duration += service_duration
        if waiting_time:
            total_duration += waiting_time.waiting_time_minutes
        
        service_sequence.append({
            'service': service,
            'duration': service_duration,
            'waiting_time': waiting_time.waiting_time_minutes if waiting_time else 0
        })
    
    return total_duration, service_sequence
```

#### **Task 2.3: Emergency Hour Extension**
**Implementation:**
```python
def extend_salon_hours(appointment_end_time, stylist_id):
    """
    Extend salon hours for appointments that run over
    """
    salon_settings = SalonSettings.get_settings()
    
    if not salon_settings.emergency_extension_enabled:
        return False
    
    # Check if appointment extends beyond salon hours
    day_name = appointment_end_time.strftime('%A').lower()
    day_hours = salon_settings.opening_hours.get(day_name, {})
    
    if day_hours.get('closed', True):
        return False
    
    closing_time = datetime.strptime(day_hours['close'], '%H:%M').time()
    
    if appointment_end_time.time() > closing_time:
        # Extend salon hours for this stylist
        return True
    
    return False
```

### **Phase 3: Customer Management System**

#### **Task 3.1: Backend Customer Addition**
**New Routes Required:**
- `/admin/customers/add` - Add new customer (admin/stylist only)
- `/admin/customers/manage` - Customer management interface
- `/admin/customers/<int:customer_id>/history` - Customer service history

**New Forms Required:**
```python
class CustomerAddForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    preferred_stylist_id = SelectField('Preferred Stylist', coerce=int, validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Add Customer')
```

#### **Task 3.2: Service History Tracking**
**Implementation:**
```python
def track_service_history(appointment):
    """
    Track service history when appointment is completed
    """
    for appointment_service in appointment.services:
        history = CustomerServiceHistory(
            customer_id=appointment.customer_id,
            service_id=appointment_service.service_id,
            appointment_id=appointment.id,
            service_date=appointment.appointment_date,
            stylist_id=appointment.stylist_id,
            actual_duration_minutes=appointment_service.end_time - appointment_service.start_time,
            notes=appointment.notes
        )
        db.session.add(history)
    
    db.session.commit()
```

#### **Task 3.3: Previous Service Suggestions**
**Implementation:**
```python
def get_customer_service_suggestions(customer_id):
    """
    Get customer's previous services for booking suggestions
    """
    # Get customer's service history
    history = CustomerServiceHistory.query.filter_by(customer_id=customer_id)\
        .order_by(CustomerServiceHistory.service_date.desc())\
        .limit(10).all()
    
    # Group by service and count frequency
    service_counts = {}
    for record in history:
        service_id = record.service_id
        if service_id not in service_counts:
            service_counts[service_id] = {
                'service': record.service,
                'count': 0,
                'last_date': record.service_date
            }
        service_counts[service_id]['count'] += 1
    
    # Return most frequent services
    return sorted(service_counts.values(), key=lambda x: x['count'], reverse=True)
```

### **Phase 4: Stylist View Enhancements**

#### **Task 4.1: Global vs Personal View Toggle**
**New Routes Required:**
- `/appointments/stylist-view` - Stylist view with toggle
- `/appointments/global-view` - Global salon view
- `/api/stylist-availability` - AJAX endpoint for availability

**Implementation:**
```python
@bp.route('/stylist-view')
@login_required
@role_required('stylist')
def stylist_view():
    view_type = request.args.get('view', 'personal')  # personal or global
    
    if view_type == 'global':
        # Show all stylists' appointments
        appointments = Appointment.query.filter(
            Appointment.appointment_date >= date.today(),
            Appointment.status.in_(['confirmed', 'completed'])
        ).order_by(Appointment.appointment_date, Appointment.start_time).all()
    else:
        # Show only current stylist's appointments
        appointments = Appointment.query.filter(
            Appointment.stylist_id == current_user.id,
            Appointment.appointment_date >= date.today(),
            Appointment.status.in_(['confirmed', 'completed'])
        ).order_by(Appointment.appointment_date, Appointment.start_time).all()
    
    return render_template('appointments/stylist_view.html', 
                         appointments=appointments, 
                         view_type=view_type)
```

#### **Task 4.2: Cross-Stylist Booking**
**Implementation:**
```python
def check_stylist_availability(stylist_id, date, start_time, end_time):
    """
    Check if stylist is available for booking
    """
    conflicts = Appointment.query.filter(
        Appointment.stylist_id == stylist_id,
        Appointment.appointment_date == date,
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
    
    return conflicts is None
```

### **Phase 5: Enhanced Holiday Management**

#### **Task 5.1: Holiday Impact Analysis**
**New Routes Required:**
- `/admin/holiday-impact/<int:request_id>` - Holiday impact analysis
- `/admin/holiday-reports` - Holiday reporting dashboard

**Implementation:**
```python
def analyze_holiday_impact(holiday_request):
    """
    Analyze the impact of a holiday request
    """
    # Calculate potential lost bookings
    start_date = holiday_request.start_date
    end_date = holiday_request.end_date
    
    # Get stylist's average daily bookings
    avg_daily_bookings = Appointment.query.filter(
        Appointment.stylist_id == holiday_request.user_id,
        Appointment.appointment_date >= start_date - timedelta(days=30),
        Appointment.appointment_date < start_date,
        Appointment.status.in_(['confirmed', 'completed'])
    ).count() / 30
    
    # Calculate potential lost revenue
    avg_booking_value = db.session.query(db.func.avg(Service.price))\
        .join(AppointmentService, Service.id == AppointmentService.service_id)\
        .join(Appointment, AppointmentService.appointment_id == Appointment.id)\
        .filter(Appointment.stylist_id == holiday_request.user_id)\
        .scalar() or 0
    
    days_off = (end_date - start_date).days + 1
    potential_lost_bookings = avg_daily_bookings * days_off
    potential_lost_revenue = potential_lost_bookings * avg_booking_value
    
    # Check other staff availability
    other_staff_off = HolidayRequest.query.filter(
        HolidayRequest.user_id != holiday_request.user_id,
        HolidayRequest.status == 'approved',
        db.or_(
            db.and_(
                HolidayRequest.start_date <= end_date,
                HolidayRequest.end_date >= start_date
            )
        )
    ).all()
    
    return {
        'potential_lost_bookings': int(potential_lost_bookings),
        'potential_lost_revenue': float(potential_lost_revenue),
        'days_off': days_off,
        'other_staff_off': [hr.user.first_name + ' ' + hr.user.last_name for hr in other_staff_off]
    }
```

### **Phase 6: UI/UX Improvements**

#### **Task 6.1: Fix Broken Functionality**
**Issues to Address:**
1. **Add New User Button** - Ensure proper routing and form handling
2. **All Appointments Button** - Fix navigation and permissions
3. **Fluid Design Changes** - Implement responsive design improvements

#### **Task 6.2: Task Completion from Current Page**
**Implementation Strategy:**
- Modal dialogs for quick actions
- Inline editing capabilities
- AJAX form submissions
- Real-time updates without page refresh

#### **Task 6.3: Enhanced Navigation**
**New Features:**
- Quick action buttons on each page
- Context-sensitive menus
- Breadcrumb navigation
- Search functionality

---

## 🚀 Development Priorities

### **Immediate (Week 1-2):**
1. **Database Schema Updates**
   - Create new models for enhanced functionality
   - Write database migrations
   - Update existing models

2. **Fix Broken Functionality**
   - Fix add new user button
   - Fix all appointments navigation
   - Test existing functionality

### **Short Term (Week 3-4):**
1. **Enhanced Appointment Booking**
   - Implement multi-service booking
   - Add service timing system
   - Implement emergency hour extension

2. **Customer Management**
   - Backend customer addition
   - Service history tracking
   - Previous service suggestions

### **Medium Term (Week 5-8):**
1. **Stylist View Enhancements**
   - Global vs personal view toggle
   - Cross-stylist booking
   - Real-time availability

2. **Holiday Management**
   - Impact analysis
   - Enhanced reporting
   - Staff availability tracking

### **Long Term (Week 9-12):**
1. **UI/UX Improvements**
   - Fluid design implementation
   - Task completion from current page
   - Enhanced user experience

2. **System Optimization**
   - Performance improvements
   - Testing and bug fixes
   - Documentation updates

---

## 🧪 Testing Strategy

### **Unit Tests:**
- Model validation and relationships
- Business logic (timing calculations, impact analysis)
- Form validation and processing

### **Integration Tests:**
- Multi-service appointment booking
- Holiday impact analysis
- Cross-stylist booking workflow

### **User Acceptance Tests:**
- Stylist booking workflow
- Customer management process
- Holiday approval process
- Emergency hour extension

---

## 📊 Success Metrics

### **Functional Metrics:**
- All new requirements implemented
- No regression in existing functionality
- Performance maintained or improved

### **User Experience Metrics:**
- Reduced booking complexity
- Improved stylist efficiency
- Better customer satisfaction

### **Business Metrics:**
- Accurate holiday impact analysis
- Improved appointment utilization
- Better financial tracking

---

## 🔧 Technical Considerations

### **Database Performance:**
- Index optimization for new queries
- Efficient multi-service booking
- Optimized holiday impact calculations

### **Security:**
- Role-based access to new features
- Data validation for all new inputs
- Audit trail for customer management

### **Scalability:**
- Efficient queries for large datasets
- Caching for frequently accessed data
- Modular design for future extensions

---

## 📝 Documentation Requirements

### **User Documentation:**
- Stylist booking guide
- Customer management guide
- Holiday management guide

### **Technical Documentation:**
- API documentation for new endpoints
- Database schema documentation
- Deployment and configuration guide

### **Business Documentation:**
- Multi-service booking methodology
- Holiday impact calculation guide
- Customer service tracking guide

---

## 🎯 Next Steps

1. **Review and approve this enhanced plan**
2. **Start with Phase 1 (Database Schema Updates)**
3. **Create detailed development timeline**
4. **Set up enhanced testing environment**
5. **Begin implementation with priority fixes**

---

*This enhanced plan integrates all new requirements from `new_requirements.txt` while maintaining and improving existing functionality. It provides a structured approach to implementing the enhanced salon management system with improved user experience and business efficiency.* 