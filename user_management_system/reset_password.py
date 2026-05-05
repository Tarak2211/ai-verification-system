#!/usr/bin/env python
"""Script to reset user password"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management_system.settings')
django.setup()

from accounts.models import CustomUser

print('=' * 70)
print('PASSWORD RESET UTILITY')
print('=' * 70)

# Reset admin password
try:
    admin = CustomUser.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print('\n✓ Admin password reset successfully!')
    print('  Username: admin')
    print('  New Password: admin123')
except CustomUser.DoesNotExist:
    print('\n✗ Admin user not found. Creating new admin...')
    admin = CustomUser.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        name='Administrator',
        password='admin123',
        role='SUPER_ADMIN'
    )
    print('\n✓ Admin user created!')
    print('  Username: admin')
    print('  Password: admin123')

print('\n' + '=' * 70)
print('ALL USER CREDENTIALS')
print('=' * 70)

users = [
    ('admin', 'admin123', 'SUPER_ADMIN'),
    ('demo_admin', 'admin123', 'SUPER_ADMIN'),
    ('demo_subadmin', 'subadmin123', 'SUB_ADMIN'),
    ('subadmin1', 'test123', 'SUB_ADMIN'),
    ('gujarat_user', 'user123', 'USER'),
    ('maharashtra_user', 'user123', 'USER'),
    ('multi_state_user', 'user123', 'USER'),
    ('user1', 'test123', 'USER'),
]

print('\n{:<20} {:<15} {:<15}'.format('Username', 'Password', 'Role'))
print('-' * 70)

for username, password, role in users:
    try:
        user = CustomUser.objects.get(username=username)
        user.set_password(password)
        user.save()
        print('{:<20} {:<15} {:<15} ✓'.format(username, password, user.role))
    except CustomUser.DoesNotExist:
        print('{:<20} {:<15} {:<15} (not found)'.format(username, password, role))

print('\n' + '=' * 70)
print('✅ All passwords have been reset!')
print('=' * 70)
print('\nYou can now login at: http://localhost:8000/accounts/login/')
print('\nRecommended login:')
print('  Username: admin')
print('  Password: admin123')
print('=' * 70)
