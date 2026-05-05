#!/usr/bin/env python
"""Script to add all Indian states to the database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management_system.settings')
django.setup()

from accounts.models import State

# All 28 States and 8 Union Territories of India
indian_states = [
    # States
    {'name': 'Andhra Pradesh', 'code': 'AP'},
    {'name': 'Arunachal Pradesh', 'code': 'AR'},
    {'name': 'Assam', 'code': 'AS'},
    {'name': 'Bihar', 'code': 'BR'},
    {'name': 'Chhattisgarh', 'code': 'CG'},
    {'name': 'Goa', 'code': 'GA'},
    {'name': 'Gujarat', 'code': 'GJ'},
    {'name': 'Haryana', 'code': 'HR'},
    {'name': 'Himachal Pradesh', 'code': 'HP'},
    {'name': 'Jharkhand', 'code': 'JH'},
    {'name': 'Karnataka', 'code': 'KA'},
    {'name': 'Kerala', 'code': 'KL'},
    {'name': 'Madhya Pradesh', 'code': 'MP'},
    {'name': 'Maharashtra', 'code': 'MH'},
    {'name': 'Manipur', 'code': 'MN'},
    {'name': 'Meghalaya', 'code': 'ML'},
    {'name': 'Mizoram', 'code': 'MZ'},
    {'name': 'Nagaland', 'code': 'NL'},
    {'name': 'Odisha', 'code': 'OR'},
    {'name': 'Punjab', 'code': 'PB'},
    {'name': 'Rajasthan', 'code': 'RJ'},
    {'name': 'Sikkim', 'code': 'SK'},
    {'name': 'Tamil Nadu', 'code': 'TN'},
    {'name': 'Telangana', 'code': 'TS'},
    {'name': 'Tripura', 'code': 'TR'},
    {'name': 'Uttar Pradesh', 'code': 'UP'},
    {'name': 'Uttarakhand', 'code': 'UK'},
    {'name': 'West Bengal', 'code': 'WB'},
    
    # Union Territories
    {'name': 'Andaman and Nicobar Islands', 'code': 'AN'},
    {'name': 'Chandigarh', 'code': 'CH'},
    {'name': 'Dadra and Nagar Haveli and Daman and Diu', 'code': 'DH'},
    {'name': 'Delhi', 'code': 'DL'},
    {'name': 'Jammu and Kashmir', 'code': 'JK'},
    {'name': 'Ladakh', 'code': 'LA'},
    {'name': 'Lakshadweep', 'code': 'LD'},
    {'name': 'Puducherry', 'code': 'PY'},
]

print('=' * 70)
print('Adding All Indian States and Union Territories')
print('=' * 70)

created_count = 0
updated_count = 0
skipped_count = 0

for state_data in indian_states:
    state, created = State.objects.get_or_create(
        code=state_data['code'],
        defaults={
            'name': state_data['name'],
            'is_active': True
        }
    )
    
    if created:
        print(f'✓ Created: {state.name} ({state.code})')
        created_count += 1
    else:
        # Update name if it exists
        if state.name != state_data['name']:
            state.name = state_data['name']
            state.save()
            print(f'↻ Updated: {state.name} ({state.code})')
            updated_count += 1
        else:
            print(f'- Skipped: {state.name} ({state.code}) - Already exists')
            skipped_count += 1

print('\n' + '=' * 70)
print('Summary:')
print(f'  ✓ Created: {created_count} states')
print(f'  ↻ Updated: {updated_count} states')
print(f'  - Skipped: {skipped_count} states')
print(f'  Total: {State.objects.count()} states in database')
print('=' * 70)
print('\n✅ All Indian states are now available in the system!')
print('You can now assign these states to users.')
