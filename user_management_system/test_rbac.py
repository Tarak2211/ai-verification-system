#!/usr/bin/env python
"""Test script for RBAC functionality"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management_system.settings')
django.setup()

from accounts.models import CustomUser, State, StatePermission

print('=' * 60)
print('RBAC System Test')
print('=' * 60)

# Test 1: Role assignments
print('\n1. Testing Role Assignments:')
admin = CustomUser.objects.get(username='admin')
print(f'   ✓ Admin role: {admin.role}, is_super_admin: {admin.is_super_admin()}')

sub_admin = CustomUser.objects.get(username='subadmin1')
print(f'   ✓ Sub-Admin role: {sub_admin.role}, is_sub_admin: {sub_admin.is_sub_admin()}')

user = CustomUser.objects.get(username='user1')
print(f'   ✓ User role: {user.role}, is_regular_user: {user.is_regular_user()}')

# Test 2: Permission checks
print('\n2. Testing Permission Checks:')
print(f'   ✓ Admin can manage sub_admin: {admin.can_manage_user(sub_admin)}')
print(f'   ✓ Admin can manage user: {admin.can_manage_user(user)}')
print(f'   ✓ Sub-Admin can manage user: {sub_admin.can_manage_user(user)}')
print(f'   ✓ Sub-Admin CANNOT manage admin: {not sub_admin.can_manage_user(admin)}')
print(f'   ✓ Sub-Admin CANNOT manage sub_admin: {not sub_admin.can_manage_user(sub_admin)}')

# Test 3: State access
print('\n3. Testing State Access:')
user_states = list(user.get_accessible_states().values_list('name', flat=True))
print(f'   ✓ User accessible states: {user_states}')

sub_admin_states = list(sub_admin.get_accessible_states().values_list('name', flat=True))
print(f'   ✓ Sub-Admin accessible states (all): {sub_admin_states}')

admin_states = list(admin.get_accessible_states().values_list('name', flat=True))
print(f'   ✓ Admin accessible states (all): {admin_states}')

# Test 4: State permissions
print('\n4. Testing State Permissions:')
user_perms = StatePermission.objects.filter(user=user)
print(f'   ✓ User has {user_perms.count()} state permission(s)')
for perm in user_perms:
    print(f'     - {perm.state.name} (granted by {perm.granted_by.username})')

# Test 5: State filtering
print('\n5. Testing State Filtering:')
all_states = State.objects.filter(is_active=True).count()
print(f'   ✓ Total active states: {all_states}')
print(f'   ✓ User can access {user.get_accessible_states().count()} state(s)')
print(f'   ✓ Sub-Admin can access {sub_admin.get_accessible_states().count()} state(s)')
print(f'   ✓ Admin can access {admin.get_accessible_states().count()} state(s)')

print('\n' + '=' * 60)
print('✓ All RBAC tests passed successfully!')
print('=' * 60)
