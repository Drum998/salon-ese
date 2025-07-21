#!/usr/bin/env python3
"""
Migration script for multi-service appointment support
- Creates AppointmentService table
- Adds new fields to Appointment and Service
- Migrates existing Appointment data to AppointmentService
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Appointment, Service, AppointmentService, User
from sqlalchemy import inspect

def table_exists(table_name):
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def migrate_appointments_multiservice():
    app = create_app()
    with app.app_context():
        print("Starting migration for multi-service appointments...")
        try:
            # 1. Create new tables/columns if not present
            if not table_exists('appointment_service'):
                print("Creating AppointmentService table...")
                AppointmentService.__table__.create(db.engine)
                print("✓ AppointmentService table created")
            else:
                print("AppointmentService table already exists")

            # 2. Migrate existing Appointment data
            migrated = 0
            skipped = 0
            for appt in Appointment.query.all():
                if appt.service_id:
                    # Use the old service_id and duration
                    service = Service.query.get(appt.service_id)
                    if not service:
                        print(f"❌ Appointment {appt.id} references missing service_id {appt.service_id}, skipping.")
                        skipped += 1
                        continue
                    # Use the old duration if possible, else fallback to service.duration
                    duration = (appt.end_time.hour * 60 + appt.end_time.minute) - (appt.start_time.hour * 60 + appt.start_time.minute)
                    if duration <= 0:
                        duration = service.duration
                    appt_service = AppointmentService(
                        appointment_id=appt.id,
                        service_id=service.id,
                        duration=duration,
                        waiting_time=getattr(service, 'waiting_time', None) or 0,
                        order=0
                    )
                    db.session.add(appt_service)
                    migrated += 1
                else:
                    print(f"❌ Appointment {appt.id} has no service_id, skipping.")
                    skipped += 1
            db.session.commit()
            print(f"✓ Migrated {migrated} appointments to AppointmentService.")
            if skipped:
                print(f"⚠️  Skipped {skipped} appointments due to missing service_id or service.")
            print("✓ Migration completed successfully!")
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    migrate_appointments_multiservice() 