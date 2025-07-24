# Salon ESE Changelog

## [1.3.0] - Stylist Calendar View Toggle & Enhanced UX - 2025-01-28

### 🎯 Major Features Added

#### Stylist Calendar View Toggle
- **Added**: Single-click switching between personal and global salon views
- **Purpose**: Improve stylist workflow efficiency and salon coordination
- **Features**:
  - Instant view switching without manual form submission
  - Auto-submit functionality for seamless transitions
  - Visual loading indicators during view changes
  - Enhanced user interface with tooltips and hints
  - Clean, intuitive design with removed redundant buttons

#### Enhanced User Experience
- **Added**: Loading spinner overlay during view transitions
- **Added**: Tooltips explaining Personal vs Global view differences
- **Added**: Visual feedback system for current view state
- **Added**: Streamlined interface with improved layout
- **Added**: Helpful hints and clear labeling

### 🔧 Technical Changes

#### Enhanced Template Functionality
```javascript
// Auto-submit functionality for calendar view toggle
document.addEventListener('DOMContentLoaded', function() {
    const autoSubmitInputs = document.querySelectorAll('.auto-submit');
    
    autoSubmitInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            // Get the form and submit automatically
            const form = this.closest('form');
            if (form) {
                // Show loading indicator
                const loadingSpinner = document.createElement('div');
                loadingSpinner.className = 'position-fixed top-50 start-50 translate-middle';
                loadingSpinner.innerHTML = `
                    <div class="d-flex align-items-center justify-content-center bg-white p-3 rounded shadow">
                        <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <span class="text-primary">Updating view...</span>
                    </div>
                `;
                document.body.appendChild(loadingSpinner);
                
                // Submit form after brief delay
                setTimeout(function() {
                    form.submit();
                }, 150);
            }
        });
    });
});
```

#### UI/UX Improvements
- **Removed**: Redundant "Update View" button
- **Enhanced**: Layout with better column distribution
- **Added**: Visual indicators for current view state
- **Improved**: Responsive design and accessibility

### 🛣️ Enhanced Routes

#### Stylist Calendar View
- Enhanced `/appointments/stylist-appointments` route with improved parameter handling
- Added `calendar_view` parameter support (personal/global)
- Enhanced logging with stylist information for global view

### 🎨 Enhanced Templates

#### Stylist Calendar Interface
- Updated `app/templates/appointments/stylist_calendar.html` with:
  - Auto-submit radio buttons for view switching
  - Loading indicator overlay
  - Enhanced layout and styling
  - Tooltips and helpful hints
  - Visual feedback system

### 📁 New Files Created

#### Testing
- `test_calendar_view.py` - Comprehensive test script for calendar view functionality

### 🔄 Files Modified

#### Core Application Files
- `app/routes/appointments.py` - Enhanced stylist appointments route with view toggle support
- `app/templates/appointments/stylist_calendar.html` - Complete UI/UX overhaul

#### Dependencies
- `requirements.txt` - Added requests library for testing

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

3. **Test the new features:**
   - Navigate to stylist calendar view
   - Test single-click switching between Personal and Global views
   - Verify loading indicators appear during transitions
   - Check that tooltips and hints are working

### 🧪 Testing Checklist

#### Calendar View Toggle
- [ ] Personal view shows only stylist's appointments
- [ ] Global view shows all salon appointments with stylist information
- [ ] Single-click switching works without manual form submission
- [ ] Loading indicator appears during view transitions
- [ ] Tooltips provide helpful information
- [ ] Interface is clean and intuitive

#### Enhanced UX
- [ ] No redundant "Update" button in interface
- [ ] Visual feedback for current view state
- [ ] Responsive design works on all screen sizes
- [ ] Navigation preserves view state across page changes

### 🐛 Bug Fixes

#### User Experience Issues
- **Fixed**: Redundant form submission requirement for view switching
- **Fixed**: Unclear interface with multiple update buttons
- **Fixed**: Lack of visual feedback during view transitions

### 📊 Performance Improvements

- **User Experience**: Reduced clicks required for view switching
- **Interface Responsiveness**: Immediate visual feedback
- **Code Efficiency**: Streamlined JavaScript implementation

### 🔮 Future Enhancements Planned

- **Advanced Calendar Features**: Emergency hour extension
- **Real-time Updates**: Live availability checking
- **Enhanced Filtering**: Advanced search and filter capabilities
- **Mobile Optimization**: Touch-friendly interface improvements

---

## [1.2.0] - Stylist Service Associations & Custom Waiting Times - 2025-01-28

### 🎯 Major Features Added

#### Stylist-Service Associations
- **Added**: New `StylistServiceAssociation` model for permission control
- **Purpose**: Control which stylists can perform which services
- **Features**:
  - Restrict stylist access to specific services
  - Prevent booking incompatible stylist-service combinations
  - Dynamic service filtering in booking forms
  - Complete CRUD interface for association management
- **API**: RESTful endpoint for getting stylist-allowed services

#### Custom Waiting Times for Stylist Timings
- **Added**: `custom_waiting_time` field to StylistServiceTiming model
- **Purpose**: Allow stylists to have custom waiting times per service
- **Features**:
  - Override service default waiting times per stylist
  - Auto-populate with service defaults in forms
  - Visual display of custom waiting times in management interface
  - Integration with booking system when stylist timing is enabled

#### Enhanced Booking Experience
- **Added**: Dynamic service filtering based on stylist permissions
- **Added**: Custom waiting time integration in appointment booking
- **Added**: Improved form validation and error handling
- **Added**: Better user experience with auto-populated fields

### 🔧 Technical Changes

#### New Database Models
```python
# Added to models.py
class StylistServiceAssociation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stylist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    is_allowed = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    stylist = db.relationship('User', foreign_keys=[stylist_id], backref='service_associations')
    service = db.relationship('Service', backref='stylist_associations')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('stylist_id', 'service_id', name='_stylist_service_assoc_uc'),)

# Enhanced StylistServiceTiming model
class StylistServiceTiming(db.Model):
    # ... existing fields ...
    custom_waiting_time = db.Column(db.Integer)  # Custom waiting time in minutes (optional)
```

#### Enhanced Forms
```python
# Added to forms.py
class StylistServiceAssociationForm(FlaskForm):
    stylist_id = SelectField('Stylist', validators=[DataRequired()])
    service_id = SelectField('Service', validators=[DataRequired()])
    is_allowed = BooleanField('Stylist can perform this service', default=True)
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Association')

# Enhanced StylistServiceTimingForm
class StylistServiceTimingForm(FlaskForm):
    # ... existing fields ...
    custom_waiting_time = StringField('Custom Waiting Time (minutes)', validators=[Optional()])
```

### 🛣️ New Routes Added

#### Stylist Service Association Management
- `GET /appointments/stylist-associations` - List all stylist associations
- `GET/POST /appointments/stylist-associations/new` - Add new association
- `GET/POST /appointments/stylist-associations/<id>/edit` - Edit existing association
- `POST /appointments/stylist-associations/<id>/delete` - Delete association

#### API Endpoints
- `GET /api/stylist-services/<stylist_id>` - Get services allowed for a stylist
- `GET /api/service/<service_id>` - Get service details for form auto-population

### 🎨 New Templates Added

#### Stylist Association Management
- `app/templates/appointments/stylist_associations.html` - Management interface
- `app/templates/appointments/stylist_association_form.html` - Add/edit association form

#### Enhanced Templates
- Updated `app/templates/appointments/stylist_timing_form.html` - Added custom waiting time field
- Updated `app/templates/appointments/stylist_timings.html` - Shows custom waiting times
- Updated `app/templates/appointments/book.html` - Dynamic service filtering
- Updated `app/templates/base.html` - Added "Stylist Associations" navigation link

### 📁 New Files Created

#### Migration Scripts
- `migrate_stylist_service_associations.py` - Database migration for stylist associations
- `migrate_stylist_timing_waiting_time.py` - Database migration for custom waiting times

### 🔄 Files Modified

#### Core Application Files
- `app/models.py` - Added StylistServiceAssociation model and enhanced StylistServiceTiming
- `app/forms.py` - Added StylistServiceAssociationForm and enhanced StylistServiceTimingForm
- `app/routes/appointments.py` - Added association routes and API endpoints

#### Templates
- `app/templates/appointments/stylist_timing_form.html` - Added custom waiting time field
- `app/templates/appointments/stylist_timings.html` - Added custom waiting time display
- `app/templates/appointments/book.html` - Enhanced with dynamic service filtering
- `app/templates/base.html` - Added navigation links

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
   docker exec -it salon-ese-web-1 python migrate_stylist_service_associations.py
   docker exec -it salon-ese-web-1 python migrate_stylist_timing_waiting_time.py
   ```

4. **Test the new features:**
   - Create stylist-service associations
   - Add custom waiting times to stylist timings
   - Test booking with service filtering
   - Verify custom waiting time integration

### 🧪 Testing Checklist

#### Stylist Service Associations
- [ ] "Stylist Associations" link appears in navigation (managers/owners)
- [ ] Can add new stylist-service associations
- [ ] Can edit existing associations
- [ ] Can delete associations
- [ ] Form validation works correctly

#### Custom Waiting Times
- [ ] Custom waiting time field appears in stylist timing forms
- [ ] Field auto-populates with service defaults
- [ ] Custom waiting times are saved correctly
- [ ] Custom waiting times display in management interface
- [ ] Custom waiting times integrate with booking system

#### Enhanced Booking
- [ ] Service selection filters based on stylist permissions
- [ ] Custom waiting times are applied when stylist timing is enabled
- [ ] API endpoints return correct data
- [ ] Form validation handles all edge cases

### 🐛 Bug Fixes

#### Form Validation Issues
- **Fixed**: ValueError on empty SelectField values by removing `coerce=int`
- **Fixed**: Added custom validation methods for form field validation
- **Fixed**: Enhanced route handlers to convert string data to integers properly

#### Migration Compatibility
- **Fixed**: PostgreSQL vs SQLite syntax differences in migration scripts
- **Fixed**: Added conditional queries for database-specific operations

### 📊 Performance Improvements

- **API Optimization**: Efficient service filtering endpoints
- **Form Handling**: Improved dynamic field management
- **Database Queries**: Optimized association and timing queries

### 🔮 Future Enhancements Planned

- **Advanced Permission System**: Role-based service permissions
- **Bulk Association Management**: Import/export stylist associations
- **Timing Analytics**: Advanced reporting on stylist performance
- **Service Packages**: Pre-defined service combinations with permissions

---

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
| 1.3.0 | 2025-01-28 | Stylist Calendar View Toggle & Enhanced UX |
| 1.2.0 | 2025-01-28 | Stylist Service Associations & Custom Waiting Times |
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