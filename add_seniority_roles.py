#!/usr/bin/env python3
"""
Script to add seniority roles (senior_stylist, junior_stylist) and assign them to existing users
"""
from app import create_app
from app.extensions import db
from app.models import User, Role

def add_seniority_roles():
    """Add senior_stylist and junior_stylist roles"""
    app = create_app()
    
    with app.app_context():
        print("🎯 Adding seniority roles...")
        
        # Create new roles
        new_roles = [
            {'name': 'senior_stylist', 'description': 'Senior stylist with advanced skills and experience'},
            {'name': 'junior_stylist', 'description': 'Junior stylist with basic skills and training'}
        ]
        
        for role_data in new_roles:
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = Role(**role_data)
                db.session.add(role)
                print(f"✅ Added role: {role_data['name']}")
            else:
                print(f"ℹ️  Role already exists: {role_data['name']}")
        
        db.session.commit()
        
        # Get all roles
        stylist_role = Role.query.filter_by(name='stylist').first()
        senior_stylist_role = Role.query.filter_by(name='senior_stylist').first()
        junior_stylist_role = Role.query.filter_by(name='junior_stylist').first()
        
        if not all([stylist_role, senior_stylist_role, junior_stylist_role]):
            print("❌ Required roles not found!")
            return
        
        # Get all current stylists
        stylists = User.query.join(User.roles).filter(Role.name == 'stylist').all()
        
        print(f"\n👥 Found {len(stylists)} stylists to update...")
        
        # Assign seniority roles based on username patterns or existing data
        for i, stylist in enumerate(stylists):
            # Remove the basic 'stylist' role
            if stylist_role in stylist.roles:
                stylist.roles.remove(stylist_role)
            
            # Assign seniority role based on position in list (for demo purposes)
            # In a real system, this would be based on actual seniority data
            if i < len(stylists) // 3:  # First third become senior stylists
                stylist.roles.append(senior_stylist_role)
                print(f"👨‍🎨 {stylist.first_name} {stylist.last_name} → Senior Stylist")
            elif i < 2 * len(stylists) // 3:  # Middle third stay as regular stylists
                stylist.roles.append(stylist_role)
                print(f"👩‍🎨 {stylist.first_name} {stylist.last_name} → Stylist")
            else:  # Last third become junior stylists
                stylist.roles.append(junior_stylist_role)
                print(f"👶 {stylist.first_name} {stylist.last_name} → Junior Stylist")
        
        db.session.commit()
        print("\n✅ Seniority roles assigned successfully!")
        
        # Show summary
        print("\n📊 Role Summary:")
        for role_name in ['owner', 'manager', 'senior_stylist', 'stylist', 'junior_stylist']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                users = User.query.join(User.roles).filter(Role.name == role_name).all()
                print(f"  {role_name.title()}: {len(users)} users")

if __name__ == '__main__':
    add_seniority_roles() 