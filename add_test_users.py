#!/usr/bin/env python3
"""
Script to add test users: 1 manager, 3 stylists, 5 customers.
Usernames: manager_1, stylist_1, stylist_2, stylist_3, cust_1 ... cust_5
All emails are dummy, all passwords are '12345678'.
"""
from app import create_app
from app.extensions import db
from app.models import User, Role

def get_role(role_name):
    return Role.query.filter_by(name=role_name).first()

def add_user(username, email, first_name, last_name, password, roles):
    user = User.query.filter_by(username=username).first()
    if user:
        print(f"User {username} already exists.")
        return user
    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True
    )
    user.set_password(password)
    for role in roles:
        user.roles.append(role)
    db.session.add(user)
    print(f"Added user: {username} ({', '.join([r.name for r in roles])})")
    return user

def main():
    app = create_app()
    with app.app_context():
        manager_role = get_role('manager')
        stylist_role = get_role('stylist')
        customer_role = get_role('customer')
        if not (manager_role and stylist_role and customer_role):
            print("Required roles do not exist. Please ensure roles are seeded.")
            return
        # Add manager
        add_user(
            username='manager_1',
            email='manager_1@example.com',
            first_name='Manager',
            last_name='One',
            password='12345678',
            roles=[manager_role]
        )
        # Add stylists
        for i in range(1, 4):
            add_user(
                username=f'stylist_{i}',
                email=f'stylist_{i}@example.com',
                first_name=f'Stylist{i}',
                last_name='Test',
                password='12345678',
                roles=[stylist_role]
            )
        # Add customers
        for i in range(1, 6):
            add_user(
                username=f'cust_{i}',
                email=f'cust_{i}@example.com',
                first_name=f'Customer{i}',
                last_name='Test',
                password='12345678',
                roles=[customer_role]
            )
        db.session.commit()
        print("Test users added.")

if __name__ == '__main__':
    main() 