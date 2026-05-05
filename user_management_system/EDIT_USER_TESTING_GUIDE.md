# Edit User Functionality Testing Guide

## Overview

The Edit User page now allows Super Admins to modify user roles and state assignments. This guide covers testing the edit functionality and Sub-Admin restrictions.

## New Features Implemented

### 1. Edit User Page - Role & State Modification
**Location**: `/accounts/edit_user/<user_id>/`

**Features**:
- ✅ Role dropdown to change user role (User/Admin)
- ✅ State checkboxes to modify assigned states
- ✅ Shows current role and states in right panel
- ✅ JavaScript updates help text based on role
- ✅ Form validation ensures Users have at least one state
- ✅ Admins with no states get "All States" access

### 2. Sub-Admin Restrictions in Create User
**Location**: `/accounts/create_user/`

**Features**:
- ✅ Super Admin sees both "User" and "Admin" role options
- ✅ Sub-Admin sees only "User" role option
- ✅ Sub-Admin cannot create other Sub-Admins
- ✅ Form validation prevents Sub-Admin from creating Admins

## Testing Steps

### Test 1: Edit User Role from User to Admin
1. Login as Super Admin (`admin` / `admin123`)
2. Go to Dashboard: `http://127.0.0.1:8000/accounts/dashboard/`
3. Find a User in the list (e.g., `gujarat_user`)
4. Click the Edit button (pencil icon)
5. You should see:
   - Current Role badge in right panel
   - Current States in right panel
   - Role dropdown in form
   - State checkboxes in form
6. Change Role from "User" to "Admin"
7. Notice all state checkboxes get checked automatically
8. Click "Update User"
9. Verify:
   - Success message appears
   - User is redirected to dashboard
   - User's role badge changed to "Admin" (yellow)
   - User's states show "All States" or selected states

### Test 2: Edit User States (Add/Remove States)
1. Login as Super Admin
2. Go to Dashboard and edit a User with multiple states
3. Current states should be pre-checked in the checkboxes
4. Uncheck some states (e.g., remove Maharashtra)
5. Check new states (e.g., add Karnataka)
6. Click "Update User"
7. Verify:
   - Success message appears
   - Dashboard shows updated state list
   - User's profile shows new states

### Test 3: Edit Admin Role to User
1. Login as Super Admin
2. Edit an Admin user
3. Change Role from "Admin" to "User"
4. Notice help text changes to require at least one state
5. Ensure at least one state is checked
6. Click "Update User"
7. Verify:
   - User's role badge changed to "User" (blue)
   - User's states show only selected states

### Test 4: Edit Admin States (Restrict Access)
1. Login as Super Admin
2. Edit an Admin with "All States" access
3. Keep Role as "Admin"
4. Uncheck some states (e.g., keep only Gujarat, Maharashtra, Karnataka)
5. Click "Update User"
6. Verify:
   - Admin's states column shows specific states (not "All States")
   - Admin can only access selected states

### Test 5: Edit Admin to Have All States
1. Login as Super Admin
2. Edit an Admin with specific states
3. Keep Role as "Admin"
4. Check all state checkboxes
5. Click "Update User"
6. Verify:
   - Admin's states column shows "All States" badge
   - Admin has full access

### Test 6: Validation - User Without States
1. Login as Super Admin
2. Edit a User
3. Keep Role as "User"
4. Uncheck all states
5. Try to submit form
6. Verify:
   - Error message: "Users must be assigned to at least one state."
   - Form does not submit
   - User remains on edit page

### Test 7: Sub-Admin Creating User (Restricted)
1. First, create a Sub-Admin if you don't have one:
   - Login as Super Admin
   - Create user with Role "Admin"
   - Assign some states or leave all checked
2. Logout and login as the Sub-Admin
3. Navigate to: `http://127.0.0.1:8000/accounts/create_user/`
4. Check the Role dropdown
5. Verify:
   - Only "User" option is visible
   - "Admin" option is NOT visible
   - Cannot select "Admin" role
6. Create a user with Role "User"
7. Verify user is created successfully

### Test 8: Super Admin Creating User (Full Access)
1. Login as Super Admin
2. Navigate to: `http://127.0.0.1:8000/accounts/create_user/`
3. Check the Role dropdown
4. Verify:
   - Both "User" and "Admin" options are visible
   - Can select either role
5. Create a user with Role "Admin"
6. Verify admin user is created successfully

## Visual Examples

### Edit User Page Layout

```
┌─────────────────────────────────────────────────────────────┐
│ Edit User: john_doe                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  LEFT COLUMN (Form)          │  RIGHT COLUMN (Info)        │
│  ─────────────────────────   │  ─────────────────────────  │
│  Username: [john_doe]        │  User ID: #5                │
│  Email: [john@example.com]   │  Current Role: [User]       │
│  Full Name: [John Doe]       │  Current States:            │
│  Role: [User ▼]              │    [Gujarat] [Delhi]        │
│                              │  Date Joined: Feb 10, 2026  │
│  Assign States:              │  Last Login: Feb 12, 2026   │
│  ┌─────────────────────────┐ │                             │
│  │ ☑ Andhra Pradesh        │ │  ℹ Admin Privileges:        │
│  │ ☐ Arunachal Pradesh     │ │  As a SuperAdmin, you can   │
│  │ ☐ Assam                 │ │  modify user role and state │
│  │ ☑ Bihar                 │ │  assignments.               │
│  │ ☑ Chhattisgarh          │ │                             │
│  │ ... (scrollable)        │ │                             │
│  └─────────────────────────┘ │                             │
│  Select at least one state   │                             │
│                              │                             │
│  ☑ Account is Active         │                             │
│                              │                             │
│  [Update User] [Back]        │                             │
└─────────────────────────────────────────────────────────────┘
```

### Role Dropdown Options

**Super Admin sees:**
```
Role: [User ▼]
      ├─ User
      └─ Admin
```

**Sub-Admin sees:**
```
Role: [User ▼]
      └─ User
```

## Expected Behavior

### Edit User Form
| Action | Result |
|--------|--------|
| Change role to Admin | All states auto-checked |
| Change role to User | Help text shows "required" |
| Uncheck all states (User) | Validation error |
| Uncheck all states (Admin) | Saves as "All States" |
| Check specific states | Saves selected states only |

### Sub-Admin Restrictions
| User Type | Can Create User | Can Create Admin |
|-----------|----------------|------------------|
| Super Admin | ✅ Yes | ✅ Yes |
| Sub-Admin | ✅ Yes | ❌ No |
| User | ❌ No | ❌ No |

## Files Modified

1. ✅ `user_management_system/accounts/forms.py`
   - Updated `AdminUserEditForm` with role and states fields
   - Added validation for User role requiring states
   - Added save logic to update StatePermission records
   - Updated `AdminCreateUserForm` to restrict role choices based on current user

2. ✅ `user_management_system/accounts/views.py`
   - Updated `create_user_view` to pass current_user to form

3. ✅ `user_management_system/templates/accounts/edit_user.html`
   - Added role dropdown field
   - Added state checkboxes
   - Added current role and states display in right panel
   - Added JavaScript for dynamic help text
   - Added CSS for styling

## Technical Details

### Form Logic (AdminUserEditForm)

```python
def __init__(self, *args, **kwargs):
    # Pre-populate states with current user's states
    if self.instance.pk:
        self.fields['states'].initial = self.instance.get_accessible_states()

def save(self, commit=True):
    # Remove existing state permissions
    StatePermission.objects.filter(user=user).delete()
    
    # For Admin with no states, assign all states
    if user.role == 'SUB_ADMIN' and not states:
        states = State.objects.filter(is_active=True)
    
    # Create new state permissions
    for state in states:
        StatePermission.objects.create(user=user, state=state)
```

### Form Logic (AdminCreateUserForm)

```python
def __init__(self, *args, **kwargs):
    self.current_user = kwargs.pop('current_user', None)
    
    # Set role choices based on current user
    if self.current_user:
        if self.current_user.is_superuser:
            # Super Admin can create both User and Admin
            self.fields['role'].choices = [('USER', 'User'), ('SUB_ADMIN', 'Admin')]
        elif self.current_user.role == 'SUB_ADMIN':
            # Sub-Admin can only create User
            self.fields['role'].choices = [('USER', 'User')]
```

### JavaScript Behavior

```javascript
// On role change
roleSelect.addEventListener('change', function() {
    if (this.value === 'USER') {
        // Show required message
        statesHelpText.textContent = 'Select at least one state (required)';
        statesHelpText.style.color = '#dc3545'; // Red
    } else if (this.value === 'SUB_ADMIN') {
        // Show info message and check all states
        statesHelpText.textContent = 'All states selected by default';
        statesHelpText.style.color = '#28a745'; // Green
        stateCheckboxes.forEach(cb => cb.checked = true);
    }
});
```

## Database Changes

When editing a user:
1. Old StatePermission records are deleted
2. New StatePermission records are created based on form selection
3. If Admin has no states selected, all states are assigned
4. User role is updated in CustomUser table

## Troubleshooting

### Issue: States not pre-populated in edit form
- Check that `get_accessible_states()` method exists on CustomUser
- Verify StatePermission records exist for the user
- Check form's `__init__` method is calling `self.fields['states'].initial`

### Issue: Sub-Admin can see "Admin" option
- Verify Sub-Admin has `role='SUB_ADMIN'` in database
- Check that `current_user` is being passed to form in view
- Verify form's `__init__` method is checking `current_user.role`

### Issue: Validation not working for User without states
- Check form's `clean()` method
- Verify role value is 'USER' (uppercase)
- Check that states field is empty list

### Issue: Admin not getting "All States" after edit
- Verify save logic checks for empty states list
- Check that State.objects.filter(is_active=True) returns all states
- Verify StatePermission records are created

## Database Verification

To verify state changes after edit:

```bash
cd user_management_system
python manage.py shell
```

```python
from accounts.models import CustomUser, StatePermission

# Check user's updated role and states
user = CustomUser.objects.get(username='john_doe')
print(f"Role: {user.role}")

# Check state permissions
perms = StatePermission.objects.filter(user=user)
print(f"State count: {perms.count()}")
for perm in perms:
    print(f"  - {perm.state.name}")

# Check if admin has all states
if user.role == 'SUB_ADMIN' and perms.count() == 0:
    print("Admin has ALL STATES access")
elif user.role == 'SUB_ADMIN' and perms.count() == 36:
    print("Admin has ALL STATES access (explicit)")
else:
    print(f"User has {perms.count()} specific states")
```

## Next Steps

After testing edit functionality:
1. Test editing multiple users in sequence
2. Verify state changes reflect in user's dashboard
3. Test data filtering based on updated states
4. Verify Sub-Admin cannot escalate privileges
5. Test edge cases (editing superuser, editing self, etc.)

## URLs for Testing

- Dashboard: `http://127.0.0.1:8000/accounts/dashboard/`
- Edit User: `http://127.0.0.1:8000/accounts/edit_user/<user_id>/`
- Create User: `http://127.0.0.1:8000/accounts/create_user/`

## Success Criteria ✅

All requirements have been successfully implemented:

1. ✅ Edit user page includes role dropdown
2. ✅ Edit user page includes state checkboxes
3. ✅ Current role and states displayed in right panel
4. ✅ States pre-populated with user's current states
5. ✅ Can change user role from User to Admin and vice versa
6. ✅ Can add/remove states for any user
7. ✅ Validation ensures Users have at least one state
8. ✅ Admins with no states get "All States" access
9. ✅ Sub-Admin can only see "User" option in create form
10. ✅ Sub-Admin cannot create other Sub-Admins
11. ✅ Super Admin can create both Users and Admins
12. ✅ Form validation prevents privilege escalation

The edit functionality is complete and ready for testing!
