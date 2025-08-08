#!/usr/bin/env python3
"""
Script to check what roles currently exist in the database
"""
from app import create_app
from app.extensions import db
from app.models import User, Role

def check_roles():
    """Check what roles exist and how many users have each role"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking current roles in database...")
        
        # Get all roles
        all_roles = Role.query.all()
        print(f"\n📋 Found {len(all_roles)} roles:")
        
        for role in all_roles:
            users = User.query.join(User.roles).filter(Role.name == role.name).all()
            print(f"  - {role.name}: {len(users)} users")
            if users:
                for user in users[:5]:  # Show first 5 users
                    print(f"    * {user.first_name} {user.last_name} ({user.username})")
                if len(users) > 5:
                    print(f"    * ... and {len(users) - 5} more")
        
        # Check specifically for stylist roles
        print(f"\n🎨 Stylist-related roles:")
        stylist_roles = ['stylist', 'senior_stylist', 'junior_stylist']
        for role_name in stylist_roles:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                users = User.query.join(User.roles).filter(Role.name == role_name).all()
                print(f"  ✅ {role_name}: {len(users)} users")
            else:
                print(f"  ❌ {role_name}: Role does not exist")

if __name__ == '__main__':
    check_roles() 