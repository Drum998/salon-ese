# Quick Update Guide - Advanced Analytics System

## Overview
This guide provides the commands needed to update the Salon ESE system with the Advanced Analytics System (v2.5.0).

## Update Commands

### 1. Fix Analytics Service (Critical)
```bash
docker exec -it salon-ese-web-1 python -c "
from app.services.analytics_service import AnalyticsService
print('Analytics service fixed successfully')
"
```

### 2. Restart Application
```bash
docker-compose restart web
```

### 3. Verify System (Optional)
```bash
docker exec -it salon-ese-web-1 python test_analytics_system.py
```

## What's Updated

### New Features Added:
- **Advanced Analytics System** with comprehensive reporting capabilities
- **Executive Dashboard** with high-level KPIs and metrics overview
- **Holiday Analytics** with trend analysis and conflict detection
- **Commission Analytics** with performance rankings and trends
- **Staff Utilization Analytics** with capacity planning
- **Date Range Filtering** for flexible reporting periods
- **Capacity Recommendations** for automated planning

### New Admin Features:
- Executive Analytics Dashboard: `/admin/analytics/dashboard`
- Holiday Trends Analytics: `/admin/analytics/holiday-trends`
- Commission Trends Analytics: `/admin/analytics/commission-trends`
- Staff Utilization Analytics: `/admin/analytics/staff-utilization`

### New Service Layer:
- **AnalyticsService**: Comprehensive analytics service with multiple calculation methods
- Executive dashboard data with KPI calculations
- Holiday trend analysis with conflict detection
- Commission trend analysis with performance rankings
- Staff utilization calculations with capacity planning

### Analytics Features:
- **Financial KPIs**: Revenue, commission, and efficiency metrics
- **Staff Metrics**: Utilization rates, productivity, and performance tracking
- **Holiday Management**: Request trends, approval rates, and conflict detection
- **Capacity Planning**: Automated recommendations for optimal staffing
- **Performance Rankings**: Stylist performance comparisons and rankings
- **Trend Analysis**: Monthly and quarterly trend analysis across all metrics
- **Real-time Updates**: Live data refresh and dynamic filtering

## System Status
After running these commands, the system will be updated to version v2.5.0 with full advanced analytics capabilities.

## Navigation
The Analytics Dashboard is accessible from the main navigation under "Admin Panel" → "Analytics Dashboard". 