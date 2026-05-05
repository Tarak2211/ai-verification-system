# Sub-Admin Permissions Implementation Guide

## Overview

The complete permission system has been implemented with three distinct user levels:

## Permission Matrix

| Action | Super Admin | Sub-Admin | User |
|--------|-------------|-----------|------|
| **View Dashboard** | ✅ All users | ✅ Users only | ✅ Own info only |
| **Create User** | ✅ Yes | ✅ Yes | ❌ No |
| **Create Admin** | ✅ Yes | ❌ No | ❌ No |
| **Edit User** | ✅ Yes | ✅ Yes | ❌ No |
| **Edit Admin** | ✅ Yes | ❌ No | ❌ No |
| **Edit Super Admin** | ✅ Yes | ❌ No | ❌ No |
| **Delete User** | ✅ Yes | ❌ No | ❌ No |
| **Toggle User Status** | ✅ Yes | ❌ No | ❌ No |
| **Reset Password** | ✅ Yes | ✅ Yes (Users only) | ❌ No |
| **View All States** | ✅ Yes | ✅ Based on assignment | ❌ No |

## Detailed Permissions

### Super Admin (Full Power)
**Can do everything:**
- ✅ View all users (Super Admins, Sub-Admins, Users)
- ✅ Create Users and Sub-Admins
- ✅ Edit anyone (Super Admins, Sub-Admins, Users)
- ✅ Change roles for anyone
- ✅ Change states for anyone
- ✅ Delete any user
- ✅ Toggle active/inactive status
- ✅ Reset passwords for anyone
- ✅ Access all states

### Sub-Admin (Limited Power)
**Can manage Users only:**
- ✅ View Users only (cannot see other Sub-Admins or Super Admins in list)
- ✅ Create Users (role dropdown shows only "User" option)
- ✅ Edit Users (can change states and details)
- ❌ Cannot create Sub-Admins
- ❌ Cannot edit Sub-Admins
- ❌ Cannot edit Super Admins
- ❌ Cannot delete users
- ❌ Cannot toggle user status
- ✅ Can reset passwords for Users
- ✅ Access based on assigned states

### User (View Only)
**Can only view:**
- ✅ View own dashboard
- ✅ View own profile
- ✅ Edit own profile (name, username, image only)
- ❌ Cannot create users
- ❌ Cannot edit other users
- ❌ Cannot access admin dashboard
- ❌ Cannot change own role or states
- ✅ View data from assigned states only

## Implementation Details

### Backend Changes

**1. New Permission Function** (`views.py`):
```python
def is_admin_or_superuser(user):
    """Check if user is a superuser or sub-admin"""
    return user.is_authenticated and (user.is_superuser or user.role == 'SUB_ADMIN')
```

**2. Updated Views**:

**create_user_view**:
- Changed from `@user_passes_test(is_superuser)` to `@user_passes_test(is_admin_or_superuser)`
- Now accessible by both Super Admin and Sub-Admin
- Form restricts role choices based on current user

**edit_user_view**:
- Changed from `@user_passes_test(is_superuser)` to `@user_passes_test(is_admin_or_superuser)`
- Added permission check: Sub-Admin cannot edit other Sub-Admins or Super Admins
- Shows error message if Sub-Admin tries to edit restricted user

**dashboard_view**:
- Updated to show admin dashboard for both Super Admin and Sub-Admin
- Sub-Admin sees filtered list (Users only)
- Super Admin sees all users

**3. Dashboard Filtering**:
```python
if request.user.role == 'SUB_ADMIN':
    users = users.filter(role='USER')  # Sub-Admin sees only Users
```

### Frontend Changes

**1. Welcome Header** (`admin_dashboard.html`):
- Super Admin: "Welcome, SuperAdmin!" with crown icon
- Sub-Admin: "Welcome, Admin!" with shield icon

**2. Action Buttons**:
- Super Admin: Shows all buttons (Edit, Delete, Toggle Status, Reset Password)
- Sub-Admin: Shows only Edit and Reset Password buttons
- Buttons conditionally rendered based on `is_superuser` and `is_subadmin` flags

**3. Context Variables**:
```python
context = {
    'is_superuser': request.user.is_superuser,
    'is_subadmin': request.user.role == 'SUB_ADMIN',
    ...
}
```

## Testing Steps

### Test 1: Create a Sub-Admin
1. Login as Super Admin (`admin` / `admin123`)
2. Go to: `http://127.0.0.1:8000/accounts/create_user/`
3. Create a Sub-Admin:
   - Username: `subadmin1`
   - Email: `subadmin1@example.com`
   - Role: Admin
   - States: Select some states or leave all checked
   - Password: `Admin@123`
4. Click "Create User"
5. Verify Sub-Admin is created

### Test 2: Login as Sub-Admin
1. Logout from Super Admin
2. Login as Sub-Admin (`subadmin1` / `Admin@123`)
3. You should see:
   - "Welcome, Admin!" header (not "Welcome, SuperAdmin!")
   - Dashboard with only Users (no Sub-Admins or Super Admins)
   - Create User button available
   - Edit and Reset Password buttons for each user

### Test 3: Sub-Admin Creates User
1. While logged in as Sub-Admin
2. Click "Create Single User" or go to: `http://127.0.0.1:8000/accounts/create_user/`
3. Check the Role dropdown
4. Verify:
   - ✅ Only "User" option is visible
   - ❌ "Admin" option is NOT visible
5. Create a user:
   - Username: `testuser1`
   - Email: `testuser1@example.com`
   - Role: User (only option)
   - States: Select some states
   - Password: `User@123`
6. Click "Create User"
7. Verify user is created and appears in dashboard

### Test 4: Sub-Admin Edits User
1. While logged in as Sub-Admin
2. In the dashboard, find a User
3. Click the Edit button (pencil icon)
4. You should see the edit form with:
   - Username, Email, Name fields
   - Role dropdown
   - State checkboxes
5. Make changes (e.g., add/remove states)
6. Click "Update User"
7. Verify changes are saved

### Test 5: Sub-Admin Cannot Edit Other Sub-Admins
1. Login as Super Admin
2. Create another Sub-Admin (e.g., `subadmin2`)
3. Logout and login as `subadmin1`
4. Check the dashboard
5. Verify:
   - ✅ `subadmin2` does NOT appear in the user list
   - ✅ Only Users are visible
6. Try to access edit URL directly: `http://127.0.0.1:8000/accounts/edit_user/<subadmin2_id>/`
7. Verify:
   - ❌ Error message: "You do not have permission to edit this user."
   - ❌ Redirected to dashboard

### Test 6: Sub-Admin Cannot Delete Users
1. While logged in as Sub-Admin
2. Check the dashboard user list
3. Verify:
   - ✅ Edit button is visible
   - ✅ Reset Password button is visible
   - ❌ Delete button is NOT visible
   - ❌ Toggle Status button is NOT visible

### Test 7: Super Admin Can Edit Everyone
1. Login as Super Admin
2. Check the dashboard
3. Verify you can see:
   - ✅ All users (Super Admins, Sub-Admins, Users)
   - ✅ All action buttons (Edit, Delete, Toggle Status, Reset Password)
4. Click Edit on a Sub-Admin
5. Verify you can edit the Sub-Admin's details
6. Click Edit on a User
7. Verify you can edit the User's details

### Test 8: User Cannot Access Admin Features
1. Login as a regular User (`testuser1` / `User@123`)
2. You should see:
   - ✅ User dashboard (not admin dashboard)
   - ✅ Own profile information
   - ❌ No "Create User" button
   - ❌ No user management features
3. Try to access create user URL: `http://127.0.0.1:8000/accounts/create_user/`
4. Verify:
   - ❌ Access denied or redirected
5. Try to access edit user URL: `http://127.0.0.1:8000/accounts/edit_user/<user_id>/`
6. Verify:
   - ❌ Access denied or redirected

## Visual Differences

### Super Admin Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ 👑 Welcome, SuperAdmin!                                 │
│ Manage your users with style and efficiency            │
├─────────────────────────────────────────────────────────┤
│ User List:                                              │
│ - admin (Super Admin) [Edit][Delete][Toggle][Reset]    │
│ - subadmin1 (Admin) [Edit][Delete][Toggle][Reset]      │
│ - testuser1 (User) [Edit][Delete][Toggle][Reset]       │
└─────────────────────────────────────────────────────────┘
```

### Sub-Admin Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ 🛡️ Welcome, Admin!                                      │
│ Manage users within your scope                         │
├─────────────────────────────────────────────────────────┤
│ User List (Users only):                                 │
│ - testuser1 (User) [Edit][Reset]                       │
│ - testuser2 (User) [Edit][Reset]                       │
│ (No Sub-Admins or Super Admins visible)                │
└─────────────────────────────────────────────────────────┘
```

### User Dashboard
```
┌─────────────────────────────────────────────────────────┐
│ 👤 Welcome back, testuser1!                            │
│ Your personal dashboard awaits                         │
├─────────────────────────────────────────────────────────┤
│ Profile Overview:                                       │
│ - Role: User                                            │
│ - Assigned States: Gujarat, Maharashtra                │
│ - [Edit My Profile] button only                        │
│ (No admin features visible)                             │
└─────────────────────────────────────────────────────────┘
```

## Security Measures

### View-Level Security
1. ✅ `@login_required` decorator on all views
2. ✅ `@user_passes_test(is_admin_or_superuser)` on admin views
3. ✅ Permission checks in view logic
4. ✅ Error messages for unauthorized access

### Form-Level Security
1. ✅ Role choices restricted based on current user
2. ✅ Validation prevents privilege escalation
3. ✅ Sub-Admin cannot create Admin role

### Template-Level Security
1. ✅ Conditional rendering based on user role
2. ✅ Action buttons shown/hidden based on permissions
3. ✅ Different welcome messages for different roles

### Database-Level Security
1. ✅ QuerySet filtering for Sub-Admin
2. ✅ State-based access control
3. ✅ Audit logging for permission changes

## Files Modified

1. ✅ `accounts/views.py`
   - Added `is_admin_or_superuser()` function
   - Updated `create_user_view` decorator
   - Updated `edit_user_view` with permission checks
   - Updated `dashboard_view` with filtering

2. ✅ `templates/accounts/admin_dashboard.html`
   - Updated welcome header for Sub-Admin
   - Conditional action buttons based on role
   - Added `is_subadmin` context variable

## URLs for Testing

| Page | URL | Super Admin | Sub-Admin | User |
|------|-----|-------------|-----------|------|
| Login | `/accounts/login/` | ✅ | ✅ | ✅ |
| Dashboard | `/accounts/dashboard/` | ✅ All users | ✅ Users only | ✅ Own info |
| Create User | `/accounts/create_user/` | ✅ User+Admin | ✅ User only | ❌ |
| Edit User | `/accounts/edit_user/<id>/` | ✅ Anyone | ✅ Users only | ❌ |
| Profile | `/accounts/profile/` | ✅ | ✅ | ✅ |

## Success Criteria ✅

All requirements successfully implemented:

1. ✅ Super Admin can edit everyone (Sub-Admins and Users)
2. ✅ Sub-Admin can only create Users (not Sub-Admins)
3. ✅ Sub-Admin can only edit Users (not Sub-Admins)
4. ✅ Sub-Admin sees only Users in dashboard
5. ✅ User can only view, cannot edit anything
6. ✅ Permission checks at view level
7. ✅ Permission checks at form level
8. ✅ Permission checks at template level
9. ✅ Appropriate error messages for unauthorized access
10. ✅ Different dashboard experience for each role

The complete permission system is now implemented and ready for testing!
