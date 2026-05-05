#!/usr/bin/env python
"""Demo script showing state-based access control"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management_system.settings')
django.setup()

from accounts.models import CustomUser, State, StatePermission

print('=' * 80)
print('STATE-BASED ACCESS CONTROL DEMONSTRATION')
print('=' * 80)

# Create demo users
print('\n📝 Creating Demo Users...\n')

# 1. Create Admin (if not exists)
admin, created = CustomUser.objects.get_or_create(
    username='demo_admin',
    defaults={
        'email': 'admin@demo.com',
        'name': 'Demo Admin',
        'role': 'SUPER_ADMIN',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print('✓ Created: Demo Admin (SUPER_ADMIN)')
else:
    print('- Demo Admin already exists')

# 2. Create Gujarat User
gujarat_user, created = CustomUser.objects.get_or_create(
    username='gujarat_user',
    defaults={
        'email': 'gujarat@demo.com',
        'name': 'Gujarat User',
        'role': 'USER'
    }
)
if created:
    gujarat_user.set_password('user123')
    gujarat_user.save()
    # Assign Gujarat state
    gujarat_state = State.objects.get(code='GJ')
    StatePermission.objects.create(
        user=gujarat_user,
        state=gujarat_state,
        granted_by=admin
    )
    print('✓ Created: Gujarat User (USER) - Access: Gujarat only')
else:
    print('- Gujarat User already exists')

# 3. Create Maharashtra User
maharashtra_user, created = CustomUser.objects.get_or_create(
    username='maharashtra_user',
    defaults={
        'email': 'maharashtra@demo.com',
        'name': 'Maharashtra User',
        'role': 'USER'
    }
)
if created:
    maharashtra_user.set_password('user123')
    maharashtra_user.save()
    # Assign Maharashtra state
    maharashtra_state = State.objects.get(code='MH')
    StatePermission.objects.create(
        user=maharashtra_user,
        state=maharashtra_state,
        granted_by=admin
    )
    print('✓ Created: Maharashtra User (USER) - Access: Maharashtra only')
else:
    print('- Maharashtra User already exists')

# 4. Create Multi-State User
multi_user, created = CustomUser.objects.get_or_create(
    username='multi_state_user',
    defaults={
        'email': 'multi@demo.com',
        'name': 'Multi State User',
        'role': 'USER'
    }
)
if created:
    multi_user.set_password('user123')
    multi_user.save()
    # Assign multiple states
    StatePermission.objects.filter(user=multi_user).delete()  # Clear existing
    for code in ['DL', 'UP', 'RJ']:  # Delhi, UP, Rajasthan
        state = State.objects.get(code=code)
        StatePermission.objects.create(
            user=multi_user,
            state=state,
            granted_by=admin
        )
    print('✓ Created: Multi State User (USER) - Access: Delhi, UP, Rajasthan')
else:
    print('- Multi State User already exists')

# 5. Create Sub-Admin
sub_admin, created = CustomUser.objects.get_or_create(
    username='demo_subadmin',
    defaults={
        'email': 'subadmin@demo.com',
        'name': 'Demo Sub Admin',
        'role': 'SUB_ADMIN'
    }
)
if created:
    sub_admin.set_password('subadmin123')
    sub_admin.save()
    print('✓ Created: Demo Sub Admin (SUB_ADMIN) - Access: All states')
else:
    print('- Demo Sub Admin already exists')

# Now demonstrate access control
print('\n' + '=' * 80)
print('ACCESS CONTROL DEMONSTRATION')
print('=' * 80)

# Reload users to get fresh data
admin = CustomUser.objects.get(username='demo_admin')
gujarat_user = CustomUser.objects.get(username='gujarat_user')
maharashtra_user = CustomUser.objects.get(username='maharashtra_user')
multi_user = CustomUser.objects.get(username='multi_state_user')
sub_admin = CustomUser.objects.get(username='demo_subadmin')

print('\n1️⃣  ADMIN ACCESS (Full Access):')
print(f'   User: {admin.username} ({admin.role})')
admin_states = admin.get_accessible_states()
print(f'   ✓ Can access {admin_states.count()} states: ALL STATES')
print(f'   States: {", ".join(admin_states.values_list("name", flat=True)[:5])}... (showing first 5)')

print('\n2️⃣  SUB-ADMIN ACCESS (Full Access):')
print(f'   User: {sub_admin.username} ({sub_admin.role})')
subadmin_states = sub_admin.get_accessible_states()
print(f'   ✓ Can access {subadmin_states.count()} states: ALL STATES')
print(f'   States: {", ".join(subadmin_states.values_list("name", flat=True)[:5])}... (showing first 5)')

print('\n3️⃣  GUJARAT USER ACCESS (Restricted):')
print(f'   User: {gujarat_user.username} ({gujarat_user.role})')
gujarat_states = gujarat_user.get_accessible_states()
print(f'   ✓ Can access {gujarat_states.count()} state(s): {", ".join(gujarat_states.values_list("name", flat=True))}')
print(f'   ✗ Cannot access: Maharashtra, Delhi, Karnataka, etc.')

print('\n4️⃣  MAHARASHTRA USER ACCESS (Restricted):')
print(f'   User: {maharashtra_user.username} ({maharashtra_user.role})')
mh_states = maharashtra_user.get_accessible_states()
print(f'   ✓ Can access {mh_states.count()} state(s): {", ".join(mh_states.values_list("name", flat=True))}')
print(f'   ✗ Cannot access: Gujarat, Delhi, Karnataka, etc.')

print('\n5️⃣  MULTI-STATE USER ACCESS (Multiple States):')
print(f'   User: {multi_user.username} ({multi_user.role})')
multi_states = multi_user.get_accessible_states()
print(f'   ✓ Can access {multi_states.count()} state(s): {", ".join(multi_states.values_list("name", flat=True))}')
print(f'   ✗ Cannot access: Other states')

print('\n' + '=' * 80)
print('HOW TO USE IN YOUR VIEWS')
print('=' * 80)

print('''
# In your Django views, use this pattern:

from accounts.models import YourModel  # Your model with state field

def my_view(request):
    # Get data filtered by user's accessible states
    if request.user.is_super_admin() or request.user.is_sub_admin():
        # Admin sees all data
        data = YourModel.objects.all()
    else:
        # User sees only their state data
        accessible_states = request.user.get_accessible_states()
        data = YourModel.objects.filter(state__in=accessible_states)
    
    return render(request, 'template.html', {'data': data})

# OR use the StateFilteredManager:

from accounts.managers import StateFilteredManager

class YourModel(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    # ... other fields
    
    objects = StateFilteredManager()

# Then in views:
def my_view(request):
    data = YourModel.objects.for_user(request.user)  # Automatically filtered!
    return render(request, 'template.html', {'data': data})
''')

print('\n' + '=' * 80)
print('DEMO CREDENTIALS')
print('=' * 80)
print('''
Login at: http://localhost:8000/accounts/login/

1. Admin (Full Access):
   Username: demo_admin
   Password: admin123
   Access: All 36 states

2. Sub-Admin (Full Access):
   Username: demo_subadmin
   Password: subadmin123
   Access: All 36 states

3. Gujarat User (Restricted):
   Username: gujarat_user
   Password: user123
   Access: Gujarat only

4. Maharashtra User (Restricted):
   Username: maharashtra_user
   Password: user123
   Access: Maharashtra only

5. Multi-State User (Multiple States):
   Username: multi_state_user
   Password: user123
   Access: Delhi, Uttar Pradesh, Rajasthan
''')

print('=' * 80)
print('✅ Demo setup complete! Start the server and test:')
print('   python manage.py runserver')
print('=' * 80)
