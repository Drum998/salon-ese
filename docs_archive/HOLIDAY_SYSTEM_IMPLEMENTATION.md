# Holiday Management System Implementation

## 🎯 **Overview**

The Holiday Management System provides a complete solution for staff holiday requests and management. It includes automatic entitlement calculations based on work patterns, a streamlined approval workflow, and comprehensive admin management tools.

## ✨ **Features Implemented**

### 1. **Staff Holiday Request System**
- **Route**: `/holiday-request`
- **Purpose**: Allow stylists to submit holiday requests
- **Features**:
  - Date range selection with validation
  - Automatic calculation of requested days
  - Current quota display
  - Recent requests history
  - Form validation and error handling

### 2. **Admin Holiday Management**
- **Routes**: 
  - `/admin/holiday-requests` - View all requests
  - `/admin/holiday-requests/<id>` - View individual request
  - `/admin/holiday-requests/<id>/approve` - Approve/reject request
  - `/admin/holiday-quotas` - View all quotas
  - `/admin/holiday-quotas/<user_id>` - View user-specific summary
- **Purpose**: Complete admin control over holiday management
- **Features**:
  - Request filtering and pagination
  - Approval workflow with notes
  - Quota management and tracking
  - Usage statistics and alerts
  - Integration with HR dashboard

### 3. **Automatic Entitlement Calculations**
- **Based on**: Work patterns and weekly hours
- **UK Employment Law**: 5.6 weeks per year (28 days for full-time)
- **Calculation**: Proportional to weekly hours
- **Integration**: Automatic calculation when work patterns change

## 🗄️ **Database Models**

### HolidayQuota Model
```python
class HolidayQuota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_hours_per_week = db.Column(db.Integer, nullable=False)
    holiday_days_entitled = db.Column(db.Integer, nullable=False)
    holiday_days_taken = db.Column(db.Integer, default=0)
    holiday_days_remaining = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    user = db.relationship('User', backref='holiday_quotas')
```

### HolidayRequest Model
```python
class HolidayRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=uk_utcnow)
    updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='holiday_requests')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_holidays')
```

## 🔧 **Service Layer**

### HolidayService
```python
class HolidayService:
    @staticmethod
    def calculate_holiday_entitlement(hours_per_week):
        """Calculate holiday entitlement based on UK employment law"""
        if hours_per_week >= 37.5:  # Full-time
            return 28
        elif hours_per_week >= 20:  # Part-time
            return int((hours_per_week / 37.5) * 28)
        else:  # Reduced hours
            return int((hours_per_week / 37.5) * 28)

    @staticmethod
    def get_or_create_holiday_quota(user_id, year=None):
        """Get or create holiday quota for user"""
        if year is None:
            year = datetime.now().year
        
        quota = HolidayQuota.query.filter_by(user_id=user_id, year=year).first()
        if not quota:
            # Create new quota based on work pattern
            work_pattern = WorkPattern.query.filter_by(user_id=user_id, is_active=True).first()
            if work_pattern:
                weekly_hours = work_pattern.get_weekly_hours()
                entitled_days = HolidayService.calculate_holiday_entitlement(weekly_hours)
                
                quota = HolidayQuota(
                    user_id=user_id,
                    year=year,
                    total_hours_per_week=weekly_hours,
                    holiday_days_entitled=entitled_days,
                    holiday_days_remaining=entitled_days
                )
                db.session.add(quota)
                db.session.commit()
        
        return quota

    @staticmethod
    def validate_holiday_request(user_id, start_date, end_date):
        """Validate holiday request"""
        errors = []
        
        # Check for past dates
        if start_date < date.today():
            errors.append("Cannot request holidays in the past")
        
        # Check for overlapping requests
        overlapping = HolidayRequest.query.filter(
            and_(
                HolidayRequest.user_id == user_id,
                HolidayRequest.status.in_(['pending', 'approved']),
                or_(
                    and_(HolidayRequest.start_date <= start_date, HolidayRequest.end_date >= start_date),
                    and_(HolidayRequest.start_date <= end_date, HolidayRequest.end_date >= end_date),
                    and_(HolidayRequest.start_date >= start_date, HolidayRequest.end_date <= end_date)
                )
            )
        ).first()
        
        if overlapping:
            errors.append("You have an overlapping holiday request")
        
        # Check quota
        quota = HolidayService.get_or_create_holiday_quota(user_id)
        days_requested = (end_date - start_date).days + 1
        
        if days_requested > quota.holiday_days_remaining:
            errors.append(f"Insufficient holiday quota. You have {quota.holiday_days_remaining} days remaining")
        
        return errors

    @staticmethod
    def create_holiday_request(user_id, start_date, end_date, notes=None):
        """Create a new holiday request"""
        errors = HolidayService.validate_holiday_request(user_id, start_date, end_date)
        
        if errors:
            return None, errors
        
        days_requested = (end_date - start_date).days + 1
        
        request = HolidayRequest(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            days_requested=days_requested,
            notes=notes
        )
        
        db.session.add(request)
        db.session.commit()
        
        return request, []

    @staticmethod
    def approve_holiday_request(request_id, approved_by_id, notes=None):
        """Approve a holiday request"""
        request = HolidayRequest.query.get(request_id)
        if not request:
            return False, "Request not found"
        
        if request.status != 'pending':
            return False, "Request is not pending"
        
        # Update quota
        quota = HolidayService.get_or_create_holiday_quota(request.user_id)
        quota.holiday_days_taken += request.days_requested
        quota.holiday_days_remaining = quota.holiday_days_entitled - quota.holiday_days_taken
        
        # Update request
        request.status = 'approved'
        request.approved_by_id = approved_by_id
        request.approved_at = datetime.now()
        request.notes = notes
        
        db.session.commit()
        
        return True, "Holiday request approved successfully"

    @staticmethod
    def reject_holiday_request(request_id, rejected_by_id, notes=None):
        """Reject a holiday request"""
        request = HolidayRequest.query.get(request_id)
        if not request:
            return False, "Request not found"
        
        if request.status != 'pending':
            return False, "Request is not pending"
        
        request.status = 'rejected'
        request.approved_by_id = rejected_by_id
        request.approved_at = datetime.now()
        request.notes = notes
        
        db.session.commit()
        
        return True, "Holiday request rejected"
```

## 📝 **Forms**

### HolidayRequestForm
```python
class HolidayRequestForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    
    def validate_end_date(self, field):
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('End date must be after start date')
```

### HolidayApprovalForm
```python
class HolidayApprovalForm(FlaskForm):
    action = SelectField('Action', choices=[('approve', 'Approve'), ('reject', 'Reject')], validators=[DataRequired()])
    notes = TextAreaField('Notes')
```

### HolidayQuotaForm
```python
class HolidayQuotaForm(FlaskForm):
    holiday_days_entitled = IntegerField('Holiday Days Entitled', validators=[DataRequired(), NumberRange(min=0)])
    holiday_days_taken = IntegerField('Holiday Days Taken', validators=[DataRequired(), NumberRange(min=0)])
    notes = TextAreaField('Notes')
```

## 🛣️ **Routes**

### Staff Routes
```python
@bp.route('/holiday-request', methods=['GET', 'POST'])
@login_required
@role_required('stylist')
def holiday_request():
    """Submit a holiday request"""
    form = HolidayRequestForm()
    
    # Get user's holiday quota
    quota = HolidayService.get_or_create_holiday_quota(current_user.id)
    
    # Get recent requests
    recent_requests = HolidayService.get_user_holiday_requests(current_user.id)[:5]
    
    if form.validate_on_submit():
        # Create the holiday request
        request_obj, errors = HolidayService.create_holiday_request(
            current_user.id,
            form.start_date.data,
            form.end_date.data,
            form.notes.data
        )
        
        if request_obj:
            flash('Holiday request submitted successfully! It will be reviewed by management.', 'success')
            return redirect(url_for('main.holiday_request'))
        else:
            for error in errors:
                flash(error, 'error')
    
    return render_template('main/holiday_request.html',
                         title='Holiday Request',
                         form=form,
                         quota=quota,
                         recent_requests=recent_requests)
```

### Admin Routes
```python
@bp.route('/holiday-requests')
@login_required
@role_required('manager')
def holiday_requests():
    """View all holiday requests"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    user_id = request.args.get('user_id', type=int)
    
    # Build query
    query = HolidayRequest.query
    
    if status_filter:
        query = query.filter(HolidayRequest.status == status_filter)
    if user_id:
        query = query.filter(HolidayRequest.user_id == user_id)
    
    # Order by creation date (most recent first)
    requests = query.order_by(HolidayRequest.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/holiday_requests.html',
                         title='Holiday Requests',
                         requests=requests,
                         status_filter=status_filter,
                         user_id=user_id)

@bp.route('/holiday-requests/<int:request_id>/approve', methods=['POST'])
@login_required
@role_required('manager')
def approve_holiday_request(request_id):
    """Approve or reject a holiday request"""
    request = HolidayRequest.query.get_or_404(request_id)
    form = HolidayApprovalForm()
    
    if form.validate_on_submit():
        if form.action.data == 'approve':
            success, message = HolidayService.approve_holiday_request(
                request_id, current_user.id, form.notes.data
            )
        else:
            success, message = HolidayService.reject_holiday_request(
                request_id, current_user.id, form.notes.data
            )
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
    
    return redirect(url_for('admin.holiday_requests'))
```

## 🎨 **Templates**

### Staff Holiday Request Template
- **File**: `app/templates/main/holiday_request.html`
- **Features**:
  - Form for date selection
  - Current quota display
  - Recent requests history
  - Validation error display

### Admin Holiday Management Templates
- **Files**:
  - `app/templates/admin/holiday_requests.html` - List all requests
  - `app/templates/admin/holiday_request_detail.html` - View individual request
  - `app/templates/admin/holiday_quotas.html` - View all quotas
  - `app/templates/admin/user_holiday_summary.html` - User-specific summary

## 🔧 **Error Fixes**

### Template Error Fixes
1. **ZeroDivisionError in holiday quotas template**:
   - **Issue**: Division by zero when calculating usage percentage
   - **Fix**: Added check for `holiday_days_entitled > 0` before division

2. **UndefinedError in stylist earnings template**:
   - **Issue**: Accessing `employment_type` on None value
   - **Fix**: Added check for `employment and employment.employment_type`

3. **TypeError in HR dashboard**:
   - **Issue**: Using `.length` on integer value
   - **Fix**: Removed `.length` filter from integer field

## 🧪 **Testing**

### Manual Testing Checklist
- [ ] Staff can submit holiday requests
- [ ] Date validation works correctly
- [ ] Quota validation prevents over-requests
- [ ] Admin can view all requests
- [ ] Admin can approve/reject requests
- [ ] Quota updates correctly on approval
- [ ] HR dashboard shows holiday summary
- [ ] All template errors are resolved
- [ ] Form validation provides clear errors
- [ ] Integration with existing systems works

### Test Scenarios
1. **Valid Holiday Request**:
   - Submit request within quota
   - Verify request is created
   - Verify quota is updated on approval

2. **Invalid Holiday Request**:
   - Submit request exceeding quota
   - Submit request with past dates
   - Submit overlapping request
   - Verify proper error messages

3. **Admin Workflow**:
   - View pending requests
   - Approve request with notes
   - Reject request with notes
   - Verify status updates

## 📊 **Integration Points**

### HR Dashboard Integration
- **File**: `app/templates/admin/hr_dashboard.html`
- **Features**:
  - Holiday summary section
  - Pending requests count
  - Total entitlement and remaining days
  - Quick links to holiday management

### Stylist Dashboard Integration
- **File**: `app/templates/main/stylist_dashboard.html`
- **Features**:
  - "Request Holiday" button in quick actions
  - Links to holiday request form

### HR Service Integration
- **File**: `app/services/hr_service.py`
- **Features**:
  - `get_holiday_summary()` method
  - Integration with existing HR dashboard
  - Holiday data aggregation

## 🚀 **Deployment**

### Database Migration
The holiday system uses existing models that were already in the database schema. No additional migrations are required.

### Configuration
No additional configuration is required. The system integrates with existing:
- User authentication and roles
- Work patterns for entitlement calculations
- Employment details for staff management

### Testing Commands
```bash
# Test the holiday system
1. Login as stylist and submit holiday request
2. Login as manager and approve/reject request
3. Check holiday quotas and usage statistics
4. Verify HR dashboard integration
```

## 📈 **Business Impact**

### For Staff
- **Easy Request Submission**: Simple interface for holiday requests
- **Transparent Tracking**: Clear view of entitlements and usage
- **Quick Feedback**: Immediate status updates on requests
- **Compliance**: Automatic entitlement calculations

### For Management
- **Streamlined Approval Process**: Easy request management and approval
- **Automatic Entitlement Calculations**: No manual calculation required
- **Comprehensive Overview**: Complete holiday management in one place
- **Compliance**: Proper holiday tracking and management

### For the Business
- **Reduced Administrative Burden**: Automated calculations and tracking
- **Improved Staff Satisfaction**: Easy request process and transparency
- **Compliance**: Proper holiday management and tracking
- **Integration**: Seamless integration with existing HR systems

## 🔮 **Future Enhancements**

### Potential Improvements
1. **Holiday Calendar Integration**: Visual calendar for holiday planning
2. **Email Notifications**: Automatic notifications for request status changes
3. **Advanced Analytics**: Enhanced holiday usage analytics
4. **Bulk Operations**: Bulk approval/rejection of requests
5. **Holiday Policies**: Configurable holiday policies and rules

### Technical Enhancements
1. **API Endpoints**: REST API for mobile app integration
2. **Real-time Updates**: WebSocket integration for live updates
3. **Advanced Reporting**: Detailed holiday reports and analytics
4. **Integration**: Further integration with payroll and HR systems

---

*Implementation completed: [Current Date]*
*Version: v2.3.0*
*Next Priority: Commission Calculation System* 