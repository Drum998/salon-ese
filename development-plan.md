# Salon ESE Development Plan
## Client Requirements Integration

This document outlines the plan for integrating the client requirements from `next steps.txt` into the existing salon booking system.

---

## 📋 Client Requirements Analysis

Based on the client's requirements document, the following major features need to be implemented:

### **Core Requirements:**
1. **Salon Settings & Opening Hours Management**
2. **Staff Work Patterns & Employment Management**
3. **Holiday Management System**
4. **Enhanced Staff Management**
5. **Financial Management & Commission Tracking**

---

## 🎯 Discrete Tasks Breakdown

### **Phase 1: Foundation & Database Schema**

#### **Task 1.1: Salon Opening Hours Management**
- Create salon opening hours settings page
- Implement salon opening/closing time configuration
- Add ability to extend salon hours for appointments that run over
- Create settings management interface for salon owners

#### **Task 1.2: Work Pattern System**
- Create work pattern management system
- Implement employment type tracking (employed vs self-employed)
- Add self-employed commission percentage tracking
- Implement billing method selection (salon bills customer vs stylist bills customer)
- Create salon billing elements configuration (color, electric, etc.)

#### **Task 1.3: Database Schema Extensions**
- Add new models to support all requirements
- Create database migrations
- Update existing models as needed

### **Phase 2: Staff Management Enhancement**

#### **Task 2.1: Employment System**
- Extend User model with employment details
- Add commission tracking for self-employed staff
- Implement billing method selection
- Create job role management

#### **Task 2.2: Work Pattern Integration**
- Integrate work patterns with appointment booking
- Add availability checking based on work patterns
- Implement stylist schedule validation

### **Phase 3: Holiday Management System**

#### **Task 3.1: Holiday Quota System**
- Implement holiday quota calculation based on work hours
- Create holiday booking interface for staff
- Add holiday approval workflow for employed staff
- Implement holiday conflict detection and management

#### **Task 3.2: Management Reports**
- Create holiday overview reports
- Implement staff availability reports
- Add appointment impact analysis
- Create holiday approval reports

### **Phase 4: Financial Management**

#### **Task 4.1: Billing System**
- Implement billing element configuration
- Add commission calculation system
- Create financial reporting for management
- Implement appointment cost breakdown

---

## 🏗️ Implementation Plan

### **Phase 1: Foundation & Database Schema**

#### **Step 1: Database Schema Extensions**

**New Models Required:**

1. **SalonSettings Model**
   ```python
   class SalonSettings(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       salon_name = db.Column(db.String(100))
       opening_hours = db.Column(db.JSON)  # Store daily opening/closing times
       emergency_extension_enabled = db.Column(db.Boolean, default=True)
       created_at = db.Column(db.DateTime, default=uk_utcnow)
       updated_at = db.Column(db.DateTime, default=uk_utcnow, onupdate=uk_utcnow)
   ```

2. **WorkPattern Model**
   ```python
   class WorkPattern(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
       pattern_name = db.Column(db.String(100))
       work_schedule = db.Column(db.JSON)  # Store weekly work schedule
       is_active = db.Column(db.Boolean, default=True)
       created_at = db.Column(db.DateTime, default=uk_utcnow)
   ```

3. **EmploymentDetails Model**
   ```python
   class EmploymentDetails(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
       employment_type = db.Column(db.String(20))  # 'employed' or 'self_employed'
       commission_percentage = db.Column(db.Numeric(5, 2))  # For self-employed
       billing_method = db.Column(db.String(20))  # 'salon_bills' or 'stylist_bills'
       job_role = db.Column(db.String(100))
       created_at = db.Column(db.DateTime, default=uk_utcnow)
   ```

4. **HolidayQuota Model**
   ```python
   class HolidayQuota(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
       year = db.Column(db.Integer, nullable=False)
       total_hours_per_week = db.Column(db.Integer)
       holiday_days_entitled = db.Column(db.Integer)
       holiday_days_taken = db.Column(db.Integer, default=0)
       holiday_days_remaining = db.Column(db.Integer)
       created_at = db.Column(db.DateTime, default=uk_utcnow)
   ```

5. **HolidayRequest Model**
   ```python
   class HolidayRequest(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
       start_date = db.Column(db.Date, nullable=False)
       end_date = db.Column(db.Date, nullable=False)
       days_requested = db.Column(db.Integer)
       status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
       approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       approved_at = db.Column(db.DateTime)
       notes = db.Column(db.Text)
       created_at = db.Column(db.DateTime, default=uk_utcnow)
   ```

6. **BillingElement Model**
   ```python
   class BillingElement(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       name = db.Column(db.String(100), nullable=False)  # e.g., 'color', 'electric'
       percentage = db.Column(db.Numeric(5, 2), nullable=False)
       is_active = db.Column(db.Boolean, default=True)
       created_at = db.Column(db.DateTime, default=uk_utcnow)
   ```

#### **Step 2: Admin Settings Interface**

**New Routes Required:**
- `/admin/salon-settings` - Salon opening hours management
- `/admin/work-patterns` - Work pattern configuration
- `/admin/employment` - Employment type management
- `/admin/billing-elements` - Billing elements configuration

**New Templates Required:**
- `admin/salon_settings.html`
- `admin/work_patterns.html`
- `admin/employment.html`
- `admin/billing_elements.html`

### **Phase 2: Staff Management Enhancement**

#### **Step 3: Employment System Integration**

**Updates to Existing Models:**
- Extend User model with employment relationship
- Add employment status to user profile
- Update appointment booking to consider employment type

**New Features:**
- Commission calculation for self-employed staff
- Billing method selection in appointment booking
- Job role assignment and management

#### **Step 4: Work Pattern Integration**

**Appointment Booking Updates:**
- Check stylist availability against work patterns
- Validate appointments against salon opening hours
- Implement emergency hour extension for appointments

### **Phase 3: Holiday Management System**

#### **Step 5: Holiday System Implementation**

**Holiday Quota Algorithm:**
```python
def calculate_holiday_entitlement(hours_per_week):
    """
    Calculate holiday entitlement based on UK employment law
    Standard: 5.6 weeks per year (28 days for full-time)
    """
    if hours_per_week >= 37.5:  # Full-time
        return 28
    elif hours_per_week >= 20:  # Part-time
        return int((hours_per_week / 37.5) * 28)
    else:  # Reduced hours
        return int((hours_per_week / 37.5) * 28)
```

**Holiday Booking Features:**
- Self-employed staff: No approval required
- Employed staff: Manager approval required
- Conflict detection with other staff
- Impact analysis on salon operations

#### **Step 6: Management Reports**

**Report Types:**
- Daily staff availability report
- Holiday impact analysis
- Financial impact of staff absence
- Appointment scheduling conflicts

### **Phase 4: Financial Management**

#### **Step 7: Billing System Implementation**

**Commission Calculation:**
```python
def calculate_commission(appointment_total, commission_percentage, billing_elements):
    """
    Calculate stylist commission based on billing method and elements
    """
    if billing_method == 'salon_bills':
        return appointment_total * (commission_percentage / 100)
    else:  # stylist_bills
        salon_share = sum(element.percentage for element in billing_elements)
        return appointment_total * (salon_share / 100)
```

**Financial Features:**
- Appointment cost breakdown
- Commission tracking
- Salon revenue reporting
- Stylist earnings reports

---

## 🚀 Development Priorities

### **Immediate (Week 1-2):**
1. **Database Schema Creation**
   - Create all new models
   - Write database migrations
   - Test model relationships

2. **Salon Settings Page**
   - Create admin interface for salon settings
   - Implement opening hours configuration
   - Add emergency extension functionality

### **Short Term (Week 3-4):**
1. **Work Pattern System**
   - Create work pattern management
   - Integrate with appointment booking
   - Add availability validation

2. **Employment System**
   - Extend user management
   - Add employment type tracking
   - Implement commission tracking

### **Medium Term (Week 5-8):**
1. **Holiday Management**
   - Implement holiday quota calculation
   - Create holiday booking interface
   - Add approval workflow

2. **Management Reports**
   - Create holiday reports
   - Implement availability reports
   - Add financial impact analysis

### **Long Term (Week 9-12):**
1. **Financial Integration**
   - Complete billing system
   - Implement commission calculations
   - Create comprehensive reporting

2. **System Optimization**
   - Performance improvements
   - User experience enhancements
   - Testing and bug fixes

---

## 🧪 Testing Strategy

### **Unit Tests:**
- Model validation and relationships
- Business logic (holiday calculation, commission calculation)
- Form validation and processing

### **Integration Tests:**
- Appointment booking with new constraints
- Holiday booking workflow
- Commission calculation accuracy

### **User Acceptance Tests:**
- Salon owner workflow
- Stylist booking process
- Manager approval process
- Customer booking experience

---

## 📊 Success Metrics

### **Functional Metrics:**
- All client requirements implemented
- No regression in existing functionality
- Performance maintained or improved

### **User Experience Metrics:**
- Reduced booking conflicts
- Improved staff satisfaction
- Better management oversight

### **Business Metrics:**
- Accurate commission tracking
- Improved holiday management
- Better financial reporting

---

## 🔧 Technical Considerations

### **Database Performance:**
- Index optimization for new queries
- Efficient holiday conflict detection
- Optimized appointment availability checks

### **Security:**
- Role-based access to new features
- Data validation for all new inputs
- Audit trail for financial transactions

### **Scalability:**
- Efficient queries for large datasets
- Caching for frequently accessed data
- Modular design for future extensions

---

## 📝 Documentation Requirements

### **User Documentation:**
- Salon owner setup guide
- Stylist user manual
- Manager approval workflow guide

### **Technical Documentation:**
- API documentation for new endpoints
- Database schema documentation
- Deployment and configuration guide

### **Business Documentation:**
- Holiday calculation methodology
- Commission structure documentation
- Billing element configuration guide

---

## 🎯 Next Steps

1. **Review and approve this plan**
2. **Start with Phase 1, Step 1 (Database Schema)**
3. **Create development timeline**
4. **Set up testing environment**
5. **Begin implementation**

---

*This plan is based on the client requirements in `next steps.txt` and the current state of the salon-ese project. It provides a structured approach to implementing all requested features while maintaining system stability and performance.* 