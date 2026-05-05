# User Management System

A Django-based user management system with authentication, user profiles, and admin dashboard.

## Features

### 1. Authentication & Database Schema
- **Registration Page**: Users can create new accounts
- **Login Page**: Secure user authentication
- **Custom User Model** with fields:
  - UserID: Auto-incremental integer (Primary Key)
  - Username: Unique identifier
  - Password: Securely hashed
  - Name: User's full name
  - Email ID: Unique email address

### 2. SuperAdmin & Dashboard
- **SuperAdmin Role**: Full administrative privileges
- **Admin Dashboard**: User management interface with:
  - User table showing Username, Status, and Actions
  - Toggle Active/Inactive status
  - Edit user details
  - Delete users
  - User statistics

### 3. Data Constraints & Permissions
- **Email Immutability**: Email cannot be changed once registered
- **User Profile Editing**: Users can edit their name and username
- **Admin Privileges**: Only SuperAdmin can modify sensitive fields
- **Access Control**: Strict permission checks between Users and SuperAdmins

### 4. Password Security & Validation
- **Strong Password Validators**:
  - Minimum 8 characters, maximum 128 characters
  - Must contain both letters and numbers (alphanumeric)
  - Cannot be too similar to user information
  - Cannot be a commonly used password

### 5. Update Logic
- **Password Persistence**: When updating profile, blank password field preserves existing password
- **Selective Updates**: Only modified fields are updated

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install django
   ```

2. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Create SuperAdmin**:
   ```bash
   python manage.py create_superadmin
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**:
   - Main Application: http://127.0.0.1:8000/
   - Admin Interface: http://127.0.0.1:8000/admin/

## Usage

### For Regular Users:
1. **Register**: Create a new account at `/accounts/register/`
2. **Login**: Access your account at `/accounts/login/`
3. **Dashboard**: View your profile information
4. **Edit Profile**: Update your name and username at `/profile/`

### For SuperAdmin:
1. **Login**: Use SuperAdmin credentials
2. **Admin Dashboard**: Manage all users from the dashboard
3. **User Management**:
   - View all users with pagination
   - Toggle user active/inactive status
   - Edit user details (including email)
   - Delete users (except yourself)

## Project Structure

```
user_management_system/
├── accounts/                   # Main app
│   ├── management/            # Custom management commands
│   │   └── commands/
│   │       └── create_superadmin.py
│   ├── migrations/            # Database migrations
│   ├── admin.py              # Admin interface configuration
│   ├── forms.py              # Form definitions
│   ├── models.py             # User model
│   ├── validators.py         # Custom password validators
│   ├── views.py              # View functions
│   └── urls.py               # URL patterns
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   └── accounts/             # Account-specific templates
├── static/                   # Static files (CSS, JS, images)
├── user_management_system/   # Project settings
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI configuration
└── manage.py                 # Django management script
```

## Key URLs

- `/` - Dashboard (redirects to login if not authenticated)
- `/accounts/register/` - User registration
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/profile/` - User profile editing
- `/dashboard/` - Main dashboard (different for users vs admins)

## Security Features

- CSRF protection on all forms
- Password hashing using Django's built-in system
- Session-based authentication
- Permission-based access control
- Input validation and sanitization
- SQL injection protection through Django ORM

## Admin Features

- User status management (Active/Inactive)
- Real-time status updates via AJAX
- User search and pagination
- Comprehensive user statistics
- Safe user deletion (prevents self-deletion)
- Email modification capabilities (admin only)

## Technology Stack

- **Backend**: Django 4.2.27
- **Database**: SQLite (default, can be changed to PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5.1.3, Font Awesome 6.0.0
- **JavaScript**: Vanilla JS for AJAX interactions
- **Authentication**: Django's built-in authentication system