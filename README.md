# User Management System

A Django-based web application for managing users with role-based access control (RBAC), state-level data permissions, and stockist product data management.

---

## What Was Built

### 1. Authentication
- User registration with unique username and email validation
- Login with inactive account detection and clear error messages
- Logout
- Home page accessible to both guests and logged-in users

### 2. Custom User Model
- Auto-incremented user ID (primary key)
- Fields: username, email, name, password, profile image, role, active status
- Email is locked after registration (cannot be changed by the user)
- Profile image upload with per-user file naming

### 3. Role-Based Access Control (RBAC)
Three roles with different permissions:

| Role | Can Do |
|------|--------|
| **Super Admin** | Full access — manage all users, reset passwords, bulk create, assign states |
| **Sub Admin** | Manage regular users only — create, edit, toggle status, assign states |
| **User** | View own profile, edit name/username/photo, access assigned state data |

### 4. User Management (Admin Dashboard)
- Paginated user table (10 per page) with username, email, name, role, status, assigned states
- Create single user with role and state assignment
- Bulk create users via CSV-style text input (`username,email,name,password`)
- Edit user details (Super Admin can also change email and role)
- Delete user (cannot delete own account)
- Toggle active/inactive status via AJAX (no page reload)
- Admin password reset (direct reset without email)
- Dashboard statistics: total, active, and inactive user counts

### 5. Password Security
- Minimum 8 characters, maximum 128
- Must contain at least one letter and one number
- Cannot contain the username
- Cannot reuse any of the last 3 passwords (tracked in `PasswordHistory`)
- Self-service password reset via email with a 30-minute expiry token

### 6. State-Based Data Access
- Indian states stored as a `State` model with code and active flag
- `StatePermission` junction table links users to states (with who granted it and when)
- Permissions are cached per user for 5 minutes and invalidated on change
- Super Admins and Sub Admins see all active states; regular users see only assigned states

### 7. Stockist Data Module
- **Stockist Dashboard** — summary statistics (total records, matched, mismatches, variance) with filters by month, validation status, and division
- **Stockist List** — paginated list of stockists filtered by the user's accessible states
- **Stockist Detail** — per-stockist product match records with month and validation filters
- **Product Mismatch Report** — all non-matched records with breakdown by mismatch type
- **Data Table** — comprehensive table (50 rows/page) with filters for month, validation, division, stockist code, state, and product name search

### 8. Data Models
- `CustomUser` — extended Django user with role and profile image
- `State` — geographic state with code
- `StatePermission` — user ↔ state access grant
- `Stockist` — distributor linked to a state
- `Division` — product division (e.g., Aesthetic, Cosmeceutical)
- `Product` — master product catalog linked to a division
- `StockistProductMatch` — PDF vs Excel product comparison records with match method (Exact/Fuzzy), variance, and validation status
- `PasswordHistory` — stores last 3 password hashes per user

### 9. RBAC Decorators & Mixins
- `role_required` decorator for function-based views
- `can_manage_user_required` decorator to validate user management permissions
- `RoleRequiredMixin` and `UserManagementMixin` for class-based views
- All permission denials are logged to `logs/rbac.log`

---

## Tech Stack

- **Backend**: Django 4.2
- **Database**: SQLite (default)
- **Frontend**: Bootstrap 5, Font Awesome 6
- **Auth**: Django's built-in authentication + custom user model
- **Other**: Django cache framework (state permission caching), AJAX for status toggles

---

## Setup

```bash
pip install -r requirements.txt
cd user_management_system
python manage.py migrate
python manage.py create_superadmin
python manage.py runserver
```

Access at `http://127.0.0.1:8000/`

---

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/accounts/register/` | Registration |
| `/accounts/login/` | Login |
| `/accounts/profile/` | Edit own profile |
| `/dashboard/` | Role-based dashboard |
| `/accounts/create-user/` | Create user (admin) |
| `/accounts/bulk-create-users/` | Bulk create (super admin) |
| `/accounts/edit-user/<id>/` | Edit user (admin) |
| `/accounts/delete-user/<id>/` | Delete user (super admin) |
| `/accounts/admin-reset-password/<id>/` | Admin password reset |
| `/accounts/rbac/users/` | RBAC user list |
| `/accounts/stockist/dashboard/` | Stockist dashboard |
| `/accounts/stockist/data/table/` | Stockist data table |
| `/accounts/stockist/reports/mismatches/` | Mismatch report |

---

## 📸 Project Screenshots

### Home Page
![Home Page](images/Home%20page.png)

### Login Page
![Login Page](images/Login%20page.png)

### Admin Welcome Dashboard
![Admin Welcome Dashboard](images/Admin%20Welcome%20Dashboard.png)

### User Dashboard & Profile (2)
![User Dashboard & Profile (2)](images/UserDashboard%20%26%20Profile%20(2).png)

### User Dashboard & Profile (3)
![User Dashboard & Profile (3)](images/UserDashboard%20%26%20Profile%20(3).png)

### Create users and admins
![Create users and admins](images/Create%20users%20and%20admins.png)

### Admin assign full state automatically
![Admin assign full state automatically](images/Admin%20assign%20full%20state%20automatically.png)

### user assign only selected states
![user assign only selected states](images/user%20assign%20only%20selected%20states.png)

### User profile
![User profile](images/User%20profile.png)

### Database page
![Database page](images/Database%20page.png)

### Database page (2)
![Database page (2)](images/Database%20page%20(2).png)

### Sub-admin page
![Sub-admin page](images/Sub-admin%20page.png)

### Users & admin list
![Users & admin list](images/Users%20%26%20admin%20list.png)

### Users & admin list (2)
![Users & admin list (2)](images/Users%20%26%20admins%20list.png)

### View Database (only State selected)
![View Database(only State selected)](images/View%20Database.png)

### View Database (only State selected) (2)
![View Database(only State selected) (2)](images/View%20Database%20(2).png)