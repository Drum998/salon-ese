# Salon ESE Changelog

## [1.1.0] - Service Management Enhancements - 2025-01-27

### 🎯 Major Features Added

#### Service Waiting Times
- **Added**: `waiting_time` field to Service model for processing time tracking
- **Purpose**: Track waiting time for services like hair coloring
- **Validation**: 0-240 minutes with proper form validation
- **Display**: Waiting times shown in service cards and booking forms

#### Stylist-Specific Service Timing
- **Added**: New `StylistServiceTiming` model for custom stylist durations
- **Features**: 
  - Unique stylist-service combinations
  - Custom duration tracking per stylist per service
  - Visual time savings display
  - Active/inactive timing entries
  - Notes for timing explanations
- **Management**: Complete CRUD interface for stylist timings

#### Enhanced Appointment Booking
- **Added**: Stylist timing selection checkbox during booking
- **Added**: Multi-service appointment support (already implemented)
- **Added**: Waiting time integration in duration calculations
- **Added**: Timing options (standard vs stylist-specific)

### 🔧 Technical Changes

#### New Database Models
```python
# Added to models.py
class StylistServiceTiming(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    custom_duration = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    stylist = db.relationship('User', foreign_keys=[stylist_id], backref='service_timings')
    service = db.relationship('Service', backref='stylist_timings')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('stylist_id', 'service_id', name='_stylist_service_uc'),)
```

#### Enhanced Service Model
```python
# Added to Service model
waiting_time = db.Column(db.Integer)  # Optional waiting/processing time in minutes
```

#### New Forms
```python
# Added to forms.py
class StylistServiceTimingForm(FlaskForm):
    stylist_id = SelectField('Stylist', coerce=int, validators=[DataRequired()])
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    custom_duration = StringField('Custom Duration (minutes)', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    is_active = BooleanField('Active Timing', default=True)
    submit = SubmitField('Save Stylist Timing')

# Enhanced ServiceForm
class ServiceForm(FlaskForm):
    # ... existing fields ...
    waiting_time = StringField('Waiting Time (minutes)', validators=[Optional()])
    
# Enhanced AppointmentServiceForm
class AppointmentServiceForm(FlaskForm):
    # ... existing fields ...
    use_stylist_timing = BooleanField('Use Stylist Timing (if available)', default=False)
```

### 🛣️ New Routes Added

#### Stylist Timing Management
- `GET /appointments/stylist-timings` - List all stylist timings
- `GET/POST /appointments/stylist-timings/new` - Add new stylist timing
- `GET/POST /appointments/stylist-timings/<id>/edit` - Edit existing timing
- `POST /appointments/stylist-timings/<id>/delete` - Delete timing entry

### 🎨 New Templates Added

#### Stylist Timing Management
- `app/templates/appointments/stylist_timings.html` - Management interface with time savings display
- `app/templates/appointments/stylist_timing_form.html` - Add/edit stylist timing form

#### Enhanced Templates
- Updated `app/templates/appointments/service_form.html` - Added waiting time field
- Updated `app/templates/appointments/services.html` - Shows waiting times in service cards
- Updated `app/templates/appointments/book.html` - Added stylist timing checkbox
- Updated `app/templates/base.html` - Added "Stylist Timings" navigation link

### 📁 New Files Created

#### Migration Scripts
- `migrate_stylist_timings.py` - Database migration for stylist timing features
- `MIGRATION_GUIDE.md` - Comprehensive migration instructions for users

#### Documentation
- `CHANGELOG.md` - This changelog file

### 🔄 Files Modified

#### Core Application Files
- `app/models.py` - Added StylistServiceTiming model and enhanced Service model
- `app/forms.py` - Added StylistServiceTimingForm and enhanced existing forms
- `app/routes/appointments.py` - Added stylist timing routes and enhanced booking logic

#### Templates
- `app/templates/appointments/service_form.html` - Added waiting time field
- `app/templates/appointments/services.html` - Added waiting time display
- `app/templates/appointments/book.html` - Added stylist timing checkbox
- `app/templates/base.html` - Added navigation link

#### Documentation
- `README.md` - Comprehensive documentation of new features

### 🚀 Migration Instructions

For users updating from previous versions:

1. **Stop the current container:**
   ```bash
   docker-compose down
   ```

2. **Rebuild with latest code:**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Run migration scripts:**
   ```bash
   docker exec -it salon-ese-web-1 python migrate_appointments_multiservice.py
   docker exec -it salon-ese-web-1 python migrate_stylist_timings.py
   ```

4. **Test the new features:**
   - Add waiting times to services
   - Create stylist timing entries
   - Test appointment booking with timing options

### 🧪 Testing Checklist

#### Service Management
- [ ] Can add waiting time to services (0-240 minutes)
- [ ] Service form validates waiting time correctly
- [ ] Service cards display waiting time information
- [ ] Waiting times are included in duration calculations

#### Stylist Timing Management
- [ ] "Stylist Timings" link appears in navigation (managers/owners)
- [ ] Can add new stylist timing entries
- [ ] Can edit existing stylist timings
- [ ] Time savings are calculated and displayed correctly
- [ ] Can delete stylist timing entries
- [ ] Form validation works correctly

#### Appointment Booking
- [ ] Booking form includes stylist timing checkbox
- [ ] Can add multiple services to appointments
- [ ] Stylist timing is used when checkbox is selected
- [ ] Duration calculations include waiting times
- [ ] Multi-service appointments work correctly

### 🐛 Bug Fixes

#### Previous Issues Resolved
- **Calendar Display**: Fixed time slot filtering in week view
- **Form Validation**: Enhanced CSRF token handling for dynamic forms
- **Navigation**: Fixed broken booking button links
- **Database**: Resolved appointment booking transaction issues

### 📊 Performance Improvements

- **Database Queries**: Optimized with proper indexing and relationships
- **Form Handling**: Improved dynamic form field management
- **UI Responsiveness**: Enhanced template rendering and JavaScript

### 🔮 Future Enhancements Planned

- **Historical Timing Analysis**: Track timing trends over time
- **Automatic Timing Suggestions**: AI-powered timing recommendations
- **Service Combinations**: Pre-defined service packages with timing
- **Advanced Reporting**: Detailed timing and efficiency reports
- **Mobile App Integration**: Timing management on mobile devices

---

## [1.0.0] - Initial Release - 2025-01-20

### 🎯 Core Features
- **User Management**: Role-based authentication system
- **Appointment Booking**: Basic appointment booking and management
- **Service Management**: Add and manage salon services
- **Admin Panel**: Comprehensive user and system management
- **Calendar Views**: Week and month calendar displays
- **Multi-Service Support**: Book appointments with multiple services

### 🔧 Technical Foundation
- **Flask Framework**: Python web application framework
- **PostgreSQL Database**: Production-ready database system
- **Docker Containerization**: Easy deployment and development
- **Role-Based Access Control**: Secure permission system
- **Timezone Support**: UK timezone handling (BST/GMT)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.1.0 | 2025-01-27 | Service Management Enhancements |
| 1.0.0 | 2025-01-20 | Initial Release |

---

## Contributing

When contributing to this project, please update this changelog with:
- New features added
- Bug fixes implemented
- Breaking changes
- Performance improvements
- Documentation updates

## Support

For migration support and troubleshooting, see:
- [Migration Guide](MIGRATION_GUIDE.md)
- [README Documentation](README.md)
- [Project Issues](https://github.com/Drum998/salon-ese/issues) 