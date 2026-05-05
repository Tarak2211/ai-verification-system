# Create User Page - Role & State Selection Testing Guide (Updated)

## What Was Implemented

The existing Create User page at `/accounts/create_user/` has been enhanced with role selection and state assignment features.

## New Features

### 1. Role Selection Dropdown
- Located after the Email field
- Two options available:
  - **User** - Standard user with limited permissions
  - **Admin** - Sub-admin with elevated permissions

### 2. Dynamic State Selection
The state selection behavior changes based on the selected role:

#### For "User" Role:
- Multiple state checkboxes appear
- User MUST select at least one state (required)
- All checkboxes are unchecked by default
- User can select multiple states
- User will have access to data from selected states only

#### For "Admin" Role:
- Multiple state checkboxes appear
- ALL states are checked by default
- Admin can uncheck specific states to restrict access
- If all states remain checked, admin gets access to all states
- If some states are unchecked, admin only gets access to checked states

## How to Test

### Step 1: Access the Page
1. Log in as SuperAdmin (username: `admin`, password: `admin123`)
2. Navigate to: `http://127.0.0.1:8000/accounts/create_user/`

### Step 2: Test User Role Creation (Multiple States)
1. Fill in the form:
   - Full Name: `Multi State User`
   - Username: `multiuser1`
   - Email: `multiuser1@example.com`
   - **Role: Select "User"**
2. Notice all state checkboxes are unchecked
3. Select multiple states (e.g., "Gujarat", "Maharashtra", "Delhi")
4. Enter password: `Test@123`
5. Confirm password: `Test@123`
6. Click "Create User"
7. Verify user is created successfully

### Step 3: Test Admin Role Creation (All States by Default)
1. Fill in the form:
   - Full Name: `Full Access Admin`
   - Username: `fulladmin1`
   - Email: `fulladmin1@example.com`
   - **Role: Select "Admin"**
2. Notice ALL state checkboxes are checked automatically
3. Leave all states checked (admin will have access to all states)
4. Enter password: `Admin@123`
5. Confirm password: `Admin@123`
6. Click "Create User"
7. Verify user is created successfully

### Step 4: Test Admin Role with Restricted States
1. Fill in the form:
   - Full Name: `Limited Admin`
   - Username: `limitedadmin1`
   - Email: `limitedadmin1@example.com`
   - **Role: Select "Admin"**
2. Notice ALL state checkboxes are checked automatically
3. Uncheck some states (e.g., keep only "Gujarat", "Maharashtra", "Karnataka")
4. Enter password: `Admin@123`
5. Confirm password: `Admin@123`
6. Click "Create User"
7. Verify user is created with only selected states

### Step 5: Test Validation
1. Try creating a User without selecting any state
2. Verify you get an error: "Users must be assigned to at least one state."

### Step 6: Verify in Dashboard
1. Navigate to: `http://127.0.0.1:8000/accounts/dashboard/`
2. Check the user list table - it now has two new columns:
   - **Role**: Shows "Super Admin", "Admin", or "User"
   - **States**: Shows the specific states assigned to each user
3. Verify the newly created users appear with:
   - Correct role badges (color-coded)
   - Their assigned states displayed as badges
   - "All States" shown for admins with full access
   - Multiple state badges for users with multiple states
   - "+X more" badge if user has more than 3 states

## Expected Behavior

### User Role (USER)
- Starts with NO states selected
- Must select at least ONE state (can select multiple)
- Will see data from all selected states
- Cannot access other states' data

### Admin Role (SUB_ADMIN)
- Starts with ALL states selected by default
- Can uncheck states to restrict access
- If all states remain checked: Gets access to ALL states (shown as "All States" in dashboard)
- If some states unchecked: Gets access to checked states only
- Can create and manage User role accounts

### Dashboard Display
- **Super Admin**: Shows "Super Admin" badge and "All States"
- **Admin with all states**: Shows "Admin" badge and "All States"
- **Admin with specific states**: Shows "Admin" badge and list of states (first 3 + count)
- **User**: Shows "User" badge and list of assigned states (first 3 + count)

## Technical Details

### Files Modified
1. `user_management_system/accounts/forms.py`
   - Removed `single_state` field
   - Updated `states` field to be used for both User and Admin roles
   - Updated validation: Users must select at least one state
   - Updated save logic: Admins with no states get all states automatically

2. `user_management_system/templates/accounts/create_user.html`
   - Removed single state dropdown
   - Shows state checkboxes for both roles
   - JavaScript automatically checks all states for Admin role
   - JavaScript unchecks all states for User role
   - Dynamic help text based on role

3. `user_management_system/templates/accounts/admin_dashboard.html`
   - Added "Role" column showing user role with color-coded badges
   - Added "States" column showing assigned states
   - Shows "All States" for admins with full access
   - Shows first 3 states + count for users with many states
   - Removed "Joined" date column to make room

4. `user_management_system/accounts/views.py`
   - Updated dashboard view to prefetch state permissions for performance

### JavaScript Behavior
- On page load: Checks role and sets appropriate state selections
- When role changes to "User": Unchecks all states, shows red required message
- When role changes to "Admin": Checks all states, shows green info message
- Dynamic help text updates based on role

## Database Verification

To verify state assignments in the database:

```bash
cd user_management_system
python manage.py shell
```

```python
from accounts.models import CustomUser, StatePermission

# Check user's role and states
user = CustomUser.objects.get(username='multiuser1')
print(f"Role: {user.role}")
print(f"States: {[sp.state.name for sp in StatePermission.objects.filter(user=user)]}")

# Check admin with all states
admin = CustomUser.objects.get(username='fulladmin1')
print(f"Role: {admin.role}")
states = StatePermission.objects.filter(user=admin)
print(f"State count: {states.count()}")
print(f"Has all states: {states.count() == 36}")  # 36 Indian states
```

## Troubleshooting

### Issue: States don't auto-check for Admin
- Check browser console for JavaScript errors
- Ensure you're using a modern browser
- Try refreshing the page

### Issue: Form validation fails for User
- Ensure at least one state is selected
- Check password meets requirements
- Verify username and email are unique

### Issue: Dashboard doesn't show states
- Clear browser cache
- Check that state permissions were created in database
- Verify user has `get_accessible_states()` method

## Next Steps

After testing, you can:
1. Create users with various state combinations
2. Test login with created users
3. Verify state-based data filtering works correctly
4. Check the RBAC interface at `/accounts/rbac/users/` for additional management options
