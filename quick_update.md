# Quick Update Guide - Commission Calculation System

## Overview
This guide provides the commands needed to update the Salon ESE system with the Commission Calculation System (v2.4.0).

## Update Commands

### 1. Apply Database Migration
```bash
docker exec -it salon-ese-web-1 python migrate_commission_system.py
```

### 2. Restart Application
```bash
docker-compose restart web
```

### 3. Verify System (Optional)
```bash
docker exec -it salon-ese-web-1 python test_commission_system.py
```

## What's Updated

### New Features Added:
- **Commission Calculation System** with billing element breakdowns
- **8 Billing Elements** configured (Color, Electric, Products, Equipment, Overheads, Styling, Treatment, Other)
- **Enhanced Database Models** with commission tracking fields
- **Advanced Commission Calculations** with performance analytics
- **New Admin Routes** for commission reports and billing element management

### New Admin Features:
- Commission Reports Dashboard: `/admin/commission/reports`
- Stylist Performance Tracking: `/admin/commission/stylist-performance/<id>`
- Salon Commission Summary: `/admin/commission/salon-summary`
- Billing Elements Management: `/admin/commission/billing-elements`

## System Status
After running these commands, the system will be updated to version v2.4.0 with full commission calculation capabilities. 