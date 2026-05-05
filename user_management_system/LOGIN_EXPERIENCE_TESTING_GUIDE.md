# Login Experience Testing Guide - Role & State Display

## Overview

When users log in, they will now see their assigned role and states on both their dashboard and profile pages.

## What Was Implemented

### 1. User Dashboard (`/accounts/dashboard/`)
- Shows user's role with color-coded badge
- Shows assigned states with individual state badges
- Different display for Super Admin, Admin, and User roles

### 2. Profile Page (`/accounts/profile/`)
- Shows user's role in the account information section
- Shows assigned states with badges
- Clear indication of access level

## Display Logic

### Super Admin
- **Role Badge**: 🔴 Red "Super Admin" badge
- **States Display**: Green "All States" badge
- **Access**: Full access to all states and all features

### Admin (SUB_ADMIN)
- **Role Badge**: 🟡 Yellow "Admin" badge
- **States Display**: 
  - If no specific states assigned → Green "All States" badge
  - If specific states assigned → Individual blue state badges
- **Access**: Based on assigned states

### User (USER)
- **Role Badge**: 🔵 Blue "User" badge
- **States Display**: Individual blue state badges for each assigned state
- **Access**: Limited to assigned states only

## Testing Steps

### Test 1: Login as Super Admin
1. Navigate to: `http://127.0.0.1:8000/accounts/login/`
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. You should be redirected to the Admin Dashboard
4. Check that you see the full user management table

**To see your own role and states:**
5. Click on your profile icon or navigate to: `http://127.0.0.1:8000/accounts/profile/`
6. Verify you see:
   - Role: "Super Admin" (red badge)
   - Assigned States: "All States" (green badge)

### Test 2: Login as Admin with All States
1. First, create an admin with all states:
   - Login as Super Admin
   - Go to: `http://127.0.0.1:8000/accounts/create_user/`
   - Create user:
     - Username: `fulladmin`
     - Email: `fulladmin@example.com`
     - Role: Admin
     - States: Leave all checked (default)
     - Password: `Admin@123`
2. Logout and login as `fulladmin` / `Admin@123`
3. Navigate to dashboard or profile
4. Verify you see:
   - Role: "Admin" (yellow badge)
   - Assigned States: "All States" (green badge)

### Test 3: Login as Admin with Specific States
1. Create an admin with limited states:
   - Login as Super Admin
   - Go to: `http://127.0.0.1:8000/accounts/create_user/`
   - Create user:
     - Username: `limitedadmin`
     - Email: `limitedadmin@example.com`
     - Role: Admin
     - States: Uncheck all except Gujarat, Maharashtra, Karnataka
     - Password: `Admin@123`
2. Logout and login as `limitedadmin` / `Admin@123`
3. Navigate to dashboard: `http://127.0.0.1:8000/accounts/dashboard/`
4. Verify you see:
   - Role: "Admin" (yellow badge)
   - Assigned States: Three blue badges showing "Gujarat", "Maharashtra", "Karnataka"

### Test 4: Login as User with Single State
1. Create a user with one state:
   - Login as Super Admin
   - Go to: `http://127.0.0.1:8000/accounts/create_user/`
   - Create user:
     - Username: `gujaratuser`
     - Email: `gujaratuser@example.com`
     - Role: User
     - States: Check only Gujarat
     - Password: `User@123`
2. Logout and login as `gujaratuser` / `User@123`
3. Navigate to dashboard: `http://127.0.0.1:8000/accounts/dashboard/`
4. Verify you see:
   - Role: "User" (blue badge)
   - Assigned States: One blue badge showing "Gujarat"

### Test 5: Login as User with Multiple States
1. Create a user with multiple states:
   - Login as Super Admin
   - Go to: `http://127.0.0.1:8000/accounts/create_user/`
   - Create user:
     - Username: `multiuser`
     - Email: `multiuser@example.com`
     - Role: User
     - States: Check Gujarat, Maharashtra, Delhi, Karnataka, Tamil Nadu
     - Password: `User@123`
2. Logout and login as `multiuser` / `User@123`
3. Navigate to dashboard: `http://127.0.0.1:8000/accounts/dashboard/`
4. Verify you see:
   - Role: "User" (blue badge)
   - Assigned States: Five blue badges showing all selected states

### Test 6: Check Profile Page
For any logged-in user:
1. Navigate to: `http://127.0.0.1:8000/accounts/profile/`
2. Verify the right side panel shows:
   - Role badge (color-coded)
   - Assigned States section with badges
   - Email address
   - Member since date
   - Account status
3. Verify the note says: "Email address and role cannot be changed. Contact administrator if you need updates."

## Visual Examples

### Dashboard Display

**Super Admin View:**
```
Profile Overview
┌─────────────────────────────────────┐
│ USERNAME: admin                     │
│ FULL NAME: Super Admin              │
│ EMAIL: admin@example.com            │
│ ROLE: [Super Admin]                 │
├─────────────────────────────────────┤
│ ASSIGNED STATES: [All States]      │
│ MEMBER SINCE: January 15, 2024      │
│ ACCOUNT STATUS: [Active Account]   │
│ LAST LOGIN: Feb 12, 2026 10:30     │
└─────────────────────────────────────┘
```

**Admin with All States:**
```
Profile Overview
┌─────────────────────────────────────┐
│ USERNAME: fulladmin                 │
│ FULL NAME: Full Access Admin        │
│ EMAIL: fulladmin@example.com        │
│ ROLE: [Admin]                       │
├─────────────────────────────────────┤
│ ASSIGNED STATES: [All States]      │
│ MEMBER SINCE: February 12, 2026     │
│ ACCOUNT STATUS: [Active Account]   │
│ LAST LOGIN: Feb 12, 2026 11:00     │
└─────────────────────────────────────┘
```

**Admin with Specific States:**
```
Profile Overview
┌─────────────────────────────────────┐
│ USERNAME: limitedadmin              │
│ FULL NAME: Limited Admin            │
│ EMAIL: limitedadmin@example.com     │
│ ROLE: [Admin]                       │
├─────────────────────────────────────┤
│ ASSIGNED STATES:                    │
│ [Gujarat] [Maharashtra] [Karnataka] │
│ MEMBER SINCE: February 12, 2026     │
│ ACCOUNT STATUS: [Active Account]   │
│ LAST LOGIN: Feb 12, 2026 11:15     │
└─────────────────────────────────────┘
```

**User with Multiple States:**
```
Profile Overview
┌─────────────────────────────────────┐
│ USERNAME: multiuser                 │
│ FULL NAME: Multi State User         │
│ EMAIL: multiuser@example.com        │
│ ROLE: [User]                        │
├─────────────────────────────────────┤
│ ASSIGNED STATES:                    │
│ [Gujarat] [Maharashtra] [Delhi]     │
│ [Karnataka] [Tamil Nadu]            │
│ MEMBER SINCE: February 12, 2026     │
│ ACCOUNT STATUS: [Active Account]   │
│ LAST LOGIN: Feb 12, 2026 11:30     │
└─────────────────────────────────────┘
```

### Profile Page Display

**Account Information Panel:**
```
Account Information
─────────────────────────────────────
Role: [Admin]

Assigned States:
[Gujarat] [Maharashtra] [Karnataka]

Email: limitedadmin@example.com
Member Since: February 12, 2026
Status: [Active]

⚠ Note: Email address and role cannot 
be changed. Contact administrator if 
you need updates.
```

## Expected Behavior Summary

| User Type | Role Badge | States Display | Access Level |
|-----------|-----------|----------------|--------------|
| Super Admin | Red "Super Admin" | Green "All States" | Full access to everything |
| Admin (all states) | Yellow "Admin" | Green "All States" | Access to all states |
| Admin (specific) | Yellow "Admin" | Blue state badges | Access to selected states only |
| User | Blue "User" | Blue state badges | Access to assigned states only |

## Files Modified

1. ✅ `user_management_system/templates/accounts/user_dashboard.html`
   - Added Role display in left column
   - Added Assigned States display in right column
   - Updated Account Info modal to show role and states

2. ✅ `user_management_system/templates/accounts/profile.html`
   - Added Role display in account information panel
   - Added Assigned States display with badges
   - Updated note to mention role cannot be changed

## Troubleshooting

### Issue: States not showing
- Ensure user has states assigned in database
- Check that `get_accessible_states()` method exists on CustomUser model
- Verify StatePermission records exist for the user

### Issue: "All States" not showing for Admin
- Check if admin has any StatePermission records
- If admin has 0 StatePermission records, "All States" should display
- If admin has some StatePermission records, only those states should display

### Issue: Role badge not showing
- Verify user has `role` field set in database
- Check that role is one of: SUPER_ADMIN, SUB_ADMIN, USER
- Ensure is_superuser flag is set correctly for Super Admins

## Database Verification

To verify user's role and states in database:

```bash
cd user_management_system
python manage.py shell
```

```python
from accounts.models import CustomUser, StatePermission

# Check specific user
user = CustomUser.objects.get(username='multiuser')
print(f"Username: {user.username}")
print(f"Role: {user.role}")
print(f"Is Superuser: {user.is_superuser}")

# Check assigned states
states = user.get_accessible_states()
print(f"Assigned States: {[s.name for s in states]}")

# Check StatePermission records
perms = StatePermission.objects.filter(user=user)
print(f"StatePermission count: {perms.count()}")
for perm in perms:
    print(f"  - {perm.state.name}")
```

## Next Steps

After verifying the login experience:
1. Test data filtering based on assigned states
2. Verify users can only see data from their assigned states
3. Test admin capabilities to manage users within their state scope
4. Verify state-based access control in all features

## URLs for Testing

- Login: `http://127.0.0.1:8000/accounts/login/`
- Dashboard: `http://127.0.0.1:8000/accounts/dashboard/`
- Profile: `http://127.0.0.1:8000/accounts/profile/`
- Create User: `http://127.0.0.1:8000/accounts/create_user/`
- Logout: `http://127.0.0.1:8000/accounts/logout/`
