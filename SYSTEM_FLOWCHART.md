# User Management System - Complete Flowchart

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER MANAGEMENT SYSTEM                          │
│                   Django-Based RBAC Platform                        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
            ┌───────▼────────┐         ┌───────▼────────┐
            │  Authentication │         │  Authorization  │
            │     System      │         │   (RBAC)       │
            └───────┬────────┘         └───────┬────────┘
                    │                           │
        ┌───────────┴───────────┐      ┌───────┴────────┐
        │                       │      │                │
    ┌───▼────┐           ┌─────▼──┐  ┌▼──────────┐   ┌▼────────┐
    │ Login  │           │Register│  │State-Based│   │ Role    │
    │        │           │        │  │  Access   │   │ System  │
    └────────┘           └────────┘  └───────────┘   └─────────┘
```

## User Roles Hierarchy

```
┌──────────────────────────────────────────────────────────────┐
│                      ROLE HIERARCHY                          │
└──────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    ┌───────▼────────┐ ┌───▼──────┐ ┌─────▼──────┐
    │  SUPER ADMIN   │ │SUB ADMIN │ │    USER    │
    │  (Full Access) │ │(Limited) │ │  (Basic)   │
    └───────┬────────┘ └────┬─────┘ └─────┬──────┘
            │               │              │
            │               │              │
    • Manage all users  • Manage Users  • View profile
    • Create Sub-Admins • State access  • Edit own data
    • Delete users      • Create Users  • View dashboard
    • Reset passwords   • Edit Users    • Limited access
    • Full state access • View reports  
    • System config     
```

## 1. GUEST USER FLOW (Unauthenticated)

```
┌─────────────┐
│   VISITOR   │
│  (Guest)    │
└──────┬──────┘
       │
       ├──────────────────────────────────────────┐
       │                                          │
┌──────▼──────┐                          ┌───────▼────────┐
│  Home Page  │                          │  Login Page    │
│  (/)        │                          │  /login/       │
└──────┬──────┘                          └───────┬────────┘
       │                                         │
       │                                  ┌──────┴──────┐
       │                                  │             │
┌──────▼──────────┐                ┌─────▼─────┐  ┌────▼────────┐
│ Register Page   │                │  Success  │  │   Failed    │
│ /register/      │                │  Login    │  │  (Retry)    │
└──────┬──────────┘                └─────┬─────┘  └─────────────┘
       │                                  │
       │ Fill Form:                       │
       │ • Username                       │
       │ • Email                          │
       │ • Name                           │
       │ • Password                       │
       │                                  │
┌──────▼──────────┐                      │
│   Validation    │                      │
│   • Unique user │                      │
│   • Unique email│                      │
│   • Password    │                      │
│     strength    │                      │
└──────┬──────────┘                      │
       │                                  │
       ├──────────┐                       │
       │          │                       │
┌──────▼─────┐ ┌──▼────────┐            │
│  Success   │ │  Failed   │            │
│  Redirect  │ │  Show     │            │
│  to Login  │ │  Errors   │            │
└──────┬─────┘ └───────────┘            │
       │                                  │
       └──────────────────────────────────┘
                      │
              ┌───────▼────────┐
              │  AUTHENTICATED │
              │     USER       │
              └────────────────┘
```

## 2. AUTHENTICATED USER FLOW (Regular User)

```
┌──────────────────────────────────────────────────────────────┐
│                    REGULAR USER DASHBOARD                    │
│                      /dashboard/                             │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│   Profile   │ │   Logout    │ │  Stockist  │
│   /profile/ │ │  /logout/   │ │   Data     │
└──────┬──────┘ └─────────────┘ └─────┬──────┘
       │                               │
       │                        (If has state access)
       │                               │
┌──────▼──────────────┐         ┌──────▼──────────┐
│  Edit Profile       │         │ View Stockist   │
│  • Name             │         │ • Dashboard     │
│  • Username         │         │ • Data Table    │
│  • Profile Image    │         │ • Reports       │
│  • Password         │         │ (Filtered by    │
│  (Email locked)     │         │  state access)  │
└──────┬──────────────┘         └─────────────────┘
       │
┌──────▼──────────────┐
│  Password Reset     │
│  • Request link     │
│  • Email sent       │
│  • 30-min expiry    │
│  • History check    │
└─────────────────────┘
```

## 3. SUB-ADMIN FLOW

```
┌──────────────────────────────────────────────────────────────┐
│                    SUB-ADMIN DASHBOARD                       │
│                      /dashboard/                             │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│ View Users  │ │Create User  │ │ Edit User  │ │  RBAC    │
│ (Users only)│ │ (Users only)│ │(Users only)│ │  Views   │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘
       │               │               │             │
       │               │               │             │
       │               │               │             │
┌──────▼───────────────────────────────────────────────────────┐
│              USER MANAGEMENT CAPABILITIES                    │
│  • View user list (paginated, 10 per page)                  │
│  • Toggle user status (Active/Inactive)                     │
│  • Edit user details (name, username, profile image)        │
│  • Assign state permissions to users                        │
│  • Create new users with role assignment                    │
│  • Cannot manage Sub-Admins or Super Admins                 │
│  • State-filtered stockist data access                      │
└──────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────────────┐
│              STOCKIST DATA ACCESS                            │
│  • Dashboard with statistics                                │
│  • Stockist list (filtered by assigned states)             │
│  • Product matching data                                    │
│  • Mismatch reports                                         │
│  • Data table with filters                                  │
└─────────────────────────────────────────────────────────────┘
```

## 4. SUPER ADMIN FLOW

```
┌──────────────────────────────────────────────────────────────┐
│                  SUPER ADMIN DASHBOARD                       │
│                    /dashboard/                               │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┬────────┐
       │               │               │              │        │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐ │
│ View All    │ │Create User  │ │ Edit User  │ │  Delete  │ │
│   Users     │ │ (Any Role)  │ │ (Any User) │ │   User   │ │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘ │
       │               │               │             │        │
       │               │               │             │        │
┌──────▼───────────────────────────────────────────────────────▼──┐
│              FULL SYSTEM ADMINISTRATION                          │
│  ✓ Manage all users (Super Admins, Sub-Admins, Users)          │
│  ✓ Create users with any role                                  │
│  ✓ Edit any user (including email modification)                │
│  ✓ Delete users (except self)                                  │
│  ✓ Toggle user status (Active/Inactive)                        │
│  ✓ Reset user passwords (admin reset)                          │
│  ✓ Bulk user creation (CSV format)                             │
│  ✓ Assign/modify state permissions                             │
│  ✓ Full access to all stockist data (all states)              │
│  ✓ RBAC user management                                        │
│  ✓ View system statistics                                      │
└─────────────────────────────────────────────────────────────────┘
       │
       ├──────────────────────────────────────────┐
       │                                          │
┌──────▼──────────────┐                  ┌───────▼────────────┐
│  Bulk Operations    │                  │  Password Reset    │
│  /bulk-create/      │                  │  /admin-reset/     │
│                     │                  │                    │
│  Format:            │                  │  • Direct reset    │
│  username,email,    │                  │  • No email needed │
│  name,password      │                  │  • Instant access  │
│                     │                  │  • History saved   │
└─────────────────────┘                  └────────────────────┘
```

## 5. PASSWORD SECURITY FLOW

```
┌──────────────────────────────────────────────────────────────┐
│                  PASSWORD SECURITY SYSTEM                    │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────────┐
│ Validation  │ │   History   │ │  Reset Flow    │
└──────┬──────┘ └──────┬──────┘ └─────┬──────────┘
       │               │               │
       │               │               │
┌──────▼───────────────▼───────────────▼──────────────────────┐
│  PASSWORD REQUIREMENTS                                       │
│  • Minimum 8 characters, maximum 128                        │
│  • Must contain letters AND numbers (alphanumeric)          │
│  • Cannot be similar to user information                    │
│  • Cannot be commonly used password                         │
│  • Cannot reuse last 3 passwords                            │
│  • Securely hashed (Django's built-in system)              │
└─────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────────────┐
│  PASSWORD RESET PROCESS                                      │
│                                                              │
│  User Request → Email Sent → Token Generated (30 min)       │
│       ↓              ↓              ↓                        │
│  Click Link → Validate Token → Enter New Password           │
│       ↓              ↓              ↓                        │
│  Validate → Check History → Save & Hash → Success           │
└─────────────────────────────────────────────────────────────┘
```

## 6. RBAC (Role-Based Access Control) FLOW

```
┌──────────────────────────────────────────────────────────────┐
│                    RBAC SYSTEM FLOW                          │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────────┐
│ User List   │ │Create User  │ │  Update User   │
│ /rbac/users/│ │/rbac/create/│ │ /rbac/edit/:id/│
└──────┬──────┘ └──────┬──────┘ └─────┬──────────┘
       │               │               │
       │               │               │
       │               │               │
┌──────▼───────────────▼───────────────▼──────────────────────┐
│              RBAC FEATURES                                   │
│  • Role assignment (Super Admin, Sub-Admin, User)           │
│  • State-based permissions                                  │
│  • Multi-state access per user                             │
│  • Permission inheritance                                   │
│  • Access control validation                                │
│  • Cached permissions (5-minute cache)                      │
└─────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────────────┐
│  STATE PERMISSION MODEL                                      │
│                                                              │
│  User ←→ StatePermission ←→ State                           │
│    ↓           ↓              ↓                              │
│  Can access  Granted by    Geographic                       │
│  stockist    Admin user     region                          │
│  data from   Timestamp      (e.g., Maharashtra)             │
│  assigned                                                    │
│  states                                                      │
└─────────────────────────────────────────────────────────────┘
```

## 7. STOCKIST DATA MANAGEMENT FLOW

```
┌──────────────────────────────────────────────────────────────┐
│              STOCKIST DATA SYSTEM                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│  Dashboard  │ │Stockist List│ │  Detail    │ │  Reports │
│ /stockist/  │ │  /list/     │ │ /:code/    │ │/reports/ │
│ dashboard/  │ │             │ │            │ │          │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘
       │               │               │             │
       │               │               │             │
┌──────▼───────────────▼───────────────▼─────────────▼────────┐
│              DATA STRUCTURE                                  │
│                                                              │
│  Stockist → Product Match Records → Validation              │
│     ↓              ↓                      ↓                  │
│  Code, Name    PDF vs Excel           MATCHED               │
│  State         Product data           QUANTITY_MISMATCH     │
│  Active        Division               DIVISION_MISMATCH     │
│                Quantity               PRODUCT_NOT_FOUND     │
│                Variance                                      │
└─────────────────────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────────────┐
│  STOCKIST DATA TABLE (/stockist/data/table/)                │
│                                                              │
│  Filters:                                                    │
│  • Month/Year                                               │
│  • Validation status                                        │
│  • Division                                                 │
│  • Stockist code                                            │
│  • State                                                    │
│  • Search (product name)                                    │
│                                                              │
│  Display (50 records per page):                             │
│  • Row index                                                │
│  • Stockist code & name                                     │
│  • State                                                    │
│  • Month/Year                                               │
│  • PDF data (division, product, closing)                    │
│  • Excel data (division, product, closing)                  │
│  • Match method (Exact/Fuzzy)                               │
│  • Variance                                                 │
│  • Validation status                                        │
│  • Label & Description                                      │
└─────────────────────────────────────────────────────────────┘
```

## 8. DATA ACCESS CONTROL FLOW

```
┌──────────────────────────────────────────────────────────────┐
│              STATE-BASED ACCESS CONTROL                      │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │
            ┌──────────▼──────────┐
            │   User Request      │
            │   Stockist Data     │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Check User Role    │
            └──────────┬──────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│ Super Admin │ │  Sub-Admin  │ │    User    │
│ Full Access │ │ All States  │ │  Assigned  │
│ All States  │ │ (Active)    │ │   States   │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
            ┌──────────▼──────────┐
            │  Get Accessible     │
            │  States (Cached)    │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Filter Stockist    │
            │  Data by States     │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Return Filtered    │
            │  Results            │
            └─────────────────────┘
```

## 9. ADMIN DASHBOARD FEATURES

```
┌──────────────────────────────────────────────────────────────┐
│                  ADMIN DASHBOARD                             │
│                  /dashboard/                                 │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│ Statistics  │ │  User Table │ │  Actions   │ │  Search  │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘
       │               │               │             │
       │               │               │             │
       │               │               │             │
┌──────▼───────────────▼───────────────▼─────────────▼────────┐
│  DASHBOARD COMPONENTS                                        │
│                                                              │
│  Statistics Panel:                                           │
│  • Total users count                                        │
│  • Active users count                                       │
│  • Inactive users count                                     │
│  • Role distribution                                        │
│                                                              │
│  User Table (Paginated - 10 per page):                      │
│  • Username                                                 │
│  • Email                                                    │
│  • Name                                                     │
│  • Role                                                     │
│  • Status (Active/Inactive toggle)                          │
│  • Assigned States                                          │
│  • Date Joined                                              │
│  • Actions (Edit, Delete, Reset Password)                   │
│                                                              │
│  Quick Actions:                                             │
│  • Create User                                              │
│  • Bulk Create Users                                        │
│  • RBAC Management                                          │
│  • View Stockist Data                                       │
└─────────────────────────────────────────────────────────────┘
```

## 10. AJAX STATUS TOGGLE FLOW

```
┌──────────────────────────────────────────────────────────────┐
│              REAL-TIME STATUS TOGGLE                         │
└──────────────────────┬───────────────────────────────────────┘
                       │
            ┌──────────▼──────────┐
            │  Admin clicks       │
            │  toggle button      │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  JavaScript sends   │
            │  AJAX POST request  │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Django view        │
            │  /toggle-status/    │
            └──────────┬──────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│ Validation  │ │   Update    │ │  Response  │
│ • Not self  │ │  Database   │ │   JSON     │
│ • Has perm  │ │  is_active  │ │            │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
            ┌──────────▼──────────┐
            │  JavaScript updates │
            │  UI without reload  │
            │  • Badge color      │
            │  • Button text      │
            │  • Status display   │
            └─────────────────────┘
```

## 11. COMPLETE URL ROUTING MAP

```
┌──────────────────────────────────────────────────────────────┐
│                     URL STRUCTURE                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│   Public    │ │Authenticated│ │   Admin    │ │  RBAC    │
│    URLs     │ │    URLs     │ │   URLs     │ │  URLs    │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘
       │               │               │             │
       │               │               │             │
┌──────▼───────────────▼───────────────▼─────────────▼────────┐
│  URL MAPPINGS                                                │
│                                                              │
│  PUBLIC:                                                     │
│  /                          → Home page                      │
│  /accounts/register/        → Registration                   │
│  /accounts/login/           → Login                          │
│  /accounts/password-reset/  → Password reset request         │
│  /accounts/password-reset-confirm/<uid>/<token>/             │
│                             → Password reset confirm         │
│                                                              │
│  AUTHENTICATED:                                              │
│  /dashboard/                → Role-based dashboard           │
│  /accounts/profile/         → User profile edit              │
│  /accounts/logout/          → Logout                         │
│                                                              │
│  ADMIN ONLY:                                                 │
│  /accounts/create-user/     → Create single user             │
│  /accounts/bulk-create-users/ → Bulk user creation           │
│  /accounts/edit-user/<id>/  → Edit user                      │
│  /accounts/delete-user/<id>/ → Delete user                   │
│  /accounts/toggle-status/<id>/ → Toggle user status          │
│  /accounts/admin-reset-password/<id>/ → Admin reset password │
│                                                              │
│  RBAC:                                                       │
│  /accounts/rbac/users/      → User list                      │
│  /accounts/rbac/users/create/ → Create with RBAC             │
│  /accounts/rbac/users/<id>/edit/ → Edit with RBAC            │
│                                                              │
│  STOCKIST:                                                   │
│  /accounts/stockist/dashboard/ → Stockist dashboard          │
│  /accounts/stockist/list/   → Stockist list                  │
│  /accounts/stockist/<code>/ → Stockist detail                │
│  /accounts/stockist/reports/mismatches/ → Mismatch report    │
│  /accounts/stockist/data/table/ → Data table view            │
└─────────────────────────────────────────────────────────────┘
```

## 12. DATABASE SCHEMA RELATIONSHIPS

```
┌──────────────────────────────────────────────────────────────┐
│                  DATABASE MODELS                             │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│ CustomUser  │ │    State    │ │  Stockist  │ │ Product  │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘
       │               │               │             │
       │               │               │             │
       │               │               │             │
┌──────▼───────────────▼───────────────▼─────────────▼────────┐
│  MODEL RELATIONSHIPS                                         │
│                                                              │
│  CustomUser:                                                 │
│  • id (PK, auto-increment)                                  │
│  • username (unique)                                        │
│  • email (unique, immutable after creation)                 │
│  • name                                                     │
│  • password (hashed)                                        │
│  • profile_image                                            │
│  • role (SUPER_ADMIN, SUB_ADMIN, USER)                      │
│  • is_active, is_staff, is_superuser                        │
│  • date_joined, last_login                                  │
│                                                              │
│  State:                                                      │
│  • id (PK)                                                  │
│  • name (unique)                                            │
│  • code (unique)                                            │
│  • is_active                                                │
│  • created_at, updated_at                                   │
│                                                              │
│  StatePermission (Junction Table):                          │
│  • user (FK → CustomUser)                                   │
│  • state (FK → State)                                       │
│  • granted_by (FK → CustomUser)                             │
│  • granted_at                                               │
│  • unique_together: [user, state]                           │
│                                                              │
│  Stockist:                                                   │
│  • code (unique)                                            │
│  • name                                                     │
│  • state (FK → State)                                       │
│  • is_active                                                │
│                                                              │
│  Division:                                                   │
│  • name (unique)                                            │
│  • is_active                                                │
│                                                              │
│  Product:                                                    │
│  • code (unique)                                            │
│  • name                                                     │
│  • division (FK → Division)                                 │
│  • is_active                                                │
│                                                              │
│  StockistProductMatch:                                       │
│  • stockist (FK → Stockist)                                 │
│  • month_year                                               │
│  • row_index                                                │
│  • pdf_division, pdf_product, pdf_closing                   │
│  • excel_division (FK), excel_product (FK), excel_closing   │
│  • match_method (EXACT, FUZZY)                              │
│  • variance                                                 │
│  • validation (MATCHED, QUANTITY_MISMATCH, etc.)            │
│  • label, description                                       │
│  • unique_together: [stockist, month_year, row_index]       │
│                                                              │
│  PasswordHistory:                                            │
│  • user (FK → CustomUser)                                   │
│  • password_hash                                            │
│  • created_at                                               │
│  • Keeps last 3 passwords per user                          │
└─────────────────────────────────────────────────────────────┘
```

## 13. SECURITY FEATURES FLOW

```
┌──────────────────────────────────────────────────────────────┐
│                  SECURITY LAYERS                             │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│   CSRF      │ │   Session   │ │   Input    │ │Password  │
│ Protection  │ │    Auth     │ │Validation  │ │ Hashing  │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘
       │               │               │             │
       │               │               │             │
┌──────▼───────────────▼───────────────▼─────────────▼────────┐
│  SECURITY IMPLEMENTATIONS                                    │
│                                                              │
│  1. CSRF Protection:                                         │
│     • All forms include {% csrf_token %}                    │
│     • POST requests validated                               │
│     • AJAX requests include CSRF header                     │
│                                                              │
│  2. Authentication:                                          │
│     • Session-based authentication                          │
│     • @login_required decorators                            │
│     • @user_passes_test for role checks                     │
│     • Automatic session expiry                              │
│                                                              │
│  3. Input Validation:                                        │
│     • Django forms with validators                          │
│     • RegexValidator for username                           │
│     • Email validation                                      │
│     • SQL injection protection (Django ORM)                 │
│     • XSS protection (template escaping)                    │
│                                                              │
│  4. Password Security:                                       │
│     • PBKDF2 hashing algorithm                              │
│     • Salt added automatically                              │
│     • Password history (last 3)                             │
│     • Strength validation                                   │
│     • Reset token expiry (30 minutes)                       │
│                                                              │
│  5. Access Control:                                          │
│     • Role-based permissions                                │
│     • State-based data filtering                            │
│     • Permission caching (5 minutes)                        │
│     • Self-action prevention (delete, deactivate)           │
│                                                              │
│  6. Data Protection:                                         │
│     • Email immutability (after creation)                   │
│     • Profile image path sanitization                       │
│     • Unique constraints (username, email)                  │
│     • Database indexes for performance                      │
└─────────────────────────────────────────────────────────────┘
```

## 14. FORM VALIDATION FLOW

```
┌──────────────────────────────────────────────────────────────┐
│                  FORM VALIDATION PROCESS                     │
└──────────────────────┬───────────────────────────────────────┘
                       │
            ┌──────────▼──────────┐
            │  User submits form  │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Django Form        │
            │  receives POST data │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Field-level        │
            │  validation         │
            └──────────┬──────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│   Type      │ │   Format    │ │  Required  │
│  Checking   │ │  Validation │ │   Fields   │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
            ┌──────────▼──────────┐
            │  Custom validators  │
            │  • Unique checks    │
            │  • Password rules   │
            │  • Regex patterns   │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  Form-level         │
            │  validation         │
            │  (clean methods)    │
            └──────────┬──────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐       │
│   Valid     │ │   Invalid   │       │
│   Save data │ │   Show      │       │
│   Redirect  │ │   errors    │       │
└─────────────┘ └─────────────┘       │
                                       │
                            ┌──────────▼──────────┐
                            │  Error messages     │
                            │  displayed to user  │
                            │  Form repopulated   │
                            └─────────────────────┘
```

## 15. TECHNOLOGY STACK

```
┌──────────────────────────────────────────────────────────────┐
│                  TECHNOLOGY STACK                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│   Backend   │ │  Database   │ │  Frontend  │ │Security  │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘
       │               │               │             │
       │               │               │             │
       │               │               │             │
┌──────▼───────────────▼───────────────▼─────────────▼────────┐
│  STACK COMPONENTS                                            │
│                                                              │
│  Backend:                                                    │
│  • Django 4.2.27                                            │
│  • Python 3.x                                               │
│  • Django ORM                                               │
│  • Class-based views (CBV)                                  │
│  • Function-based views (FBV)                               │
│  • Django authentication system                             │
│  • Django forms                                             │
│  • Django signals                                           │
│                                                              │
│  Database:                                                   │
│  • SQLite (development)                                     │
│  • PostgreSQL/MySQL ready                                   │
│  • Django migrations                                        │
│  • Database indexes                                         │
│  • Query optimization                                       │
│                                                              │
│  Frontend:                                                   │
│  • Bootstrap 5.1.3                                          │
│  • Font Awesome 6.0.0                                       │
│  • Vanilla JavaScript                                       │
│  • AJAX for real-time updates                               │
│  • Django template engine                                   │
│  • Responsive design                                        │
│                                                              │
│  Security:                                                   │
│  • Django CSRF protection                                   │
│  • PBKDF2 password hashing                                  │
│  • Session management                                       │
│  • Permission decorators                                    │
│  • Input sanitization                                       │
│  • SQL injection protection                                 │
│                                                              │
│  Caching:                                                    │
│  • Django cache framework                                   │
│  • State permission caching (5 min)                         │
│  • Query result caching                                     │
│                                                              │
│  Email:                                                      │
│  • Django email backend                                     │
│  • SMTP configuration                                       │
│  • HTML email templates                                     │
│  • Password reset emails                                    │
└─────────────────────────────────────────────────────────────┘
```

## 16. COMPLETE USER JOURNEY MAP

```
┌──────────────────────────────────────────────────────────────┐
│                  USER JOURNEY MAP                            │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │
        ┌──────────────▼──────────────┐
        │  1. DISCOVERY PHASE         │
        │  • Visit website            │
        │  • View home page           │
        │  • Learn about features     │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  2. REGISTRATION PHASE      │
        │  • Click register           │
        │  • Fill form                │
        │  • Submit                   │
        │  • Validation               │
        │  • Account created          │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  3. AUTHENTICATION PHASE    │
        │  • Navigate to login        │
        │  • Enter credentials        │
        │  • Submit                   │
        │  • Session created          │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  4. DASHBOARD PHASE         │
        │  • Role-based redirect      │
        │  • View dashboard           │
        │  • See available features   │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  5. INTERACTION PHASE       │
        │  • Manage profile           │
        │  • Access data              │
        │  • Perform actions          │
        │  • View reports             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  6. ADMINISTRATION PHASE    │
        │  (Admin users only)         │
        │  • Manage users             │
        │  • Assign permissions       │
        │  • View analytics           │
        │  • System configuration     │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  7. EXIT PHASE              │
        │  • Logout                   │
        │  • Session destroyed        │
        │  • Redirect to login        │
        └─────────────────────────────┘
```

## 17. ERROR HANDLING FLOW

```
┌──────────────────────────────────────────────────────────────┐
│                  ERROR HANDLING SYSTEM                       │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│ Validation  │ │   Auth      │ │Permission  │ │ System   │
│   Errors    │ │  Errors     │ │  Errors    │ │  Errors  │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘
       │               │               │             │
       │               │               │             │
┌──────▼───────────────▼───────────────▼─────────────▼────────┐
│  ERROR TYPES & HANDLING                                      │
│                                                              │
│  Validation Errors:                                          │
│  • Form field errors → Display inline                       │
│  • Unique constraint → "Already exists" message             │
│  • Password strength → Specific requirements shown          │
│  • Required fields → "This field is required"               │
│                                                              │
│  Authentication Errors:                                      │
│  • Invalid credentials → "Invalid username or password"     │
│  • Inactive account → "Account is inactive"                 │
│  • Session expired → Redirect to login                      │
│                                                              │
│  Permission Errors:                                          │
│  • Unauthorized access → 403 Forbidden                      │
│  • Role mismatch → "You don't have permission"              │
│  • State access denied → Filtered results                   │
│                                                              │
│  System Errors:                                              │
│  • Database errors → Generic error message                  │
│  • Email send failure → "Error sending email"               │
│  • File upload errors → "Invalid file type/size"            │
│                                                              │
│  User Feedback:                                              │
│  • Success messages (green)                                 │
│  • Error messages (red)                                     │
│  • Warning messages (yellow)                                │
│  • Info messages (blue)                                     │
│  • Django messages framework                                │
└─────────────────────────────────────────────────────────────┘
```

## 18. PAGINATION & PERFORMANCE

```
┌──────────────────────────────────────────────────────────────┐
│              PAGINATION & OPTIMIZATION                       │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│ Pagination  │ │   Caching   │ │  Database  │
│             │ │             │ │   Indexes  │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘
       │               │               │
       │               │               │
┌──────▼───────────────▼───────────────▼──────────────────────┐
│  PERFORMANCE FEATURES                                        │
│                                                              │
│  Pagination:                                                 │
│  • Admin dashboard: 10 users per page                       │
│  • Stockist list: 50 per page                               │
│  • Data table: 50 records per page                          │
│  • Product matches: 100 per page                            │
│  • Django Paginator class                                   │
│  • Page navigation controls                                 │
│                                                              │
│  Caching:                                                    │
│  • State permissions: 5-minute cache                        │
│  • Cache key: user_states_{user_id}                         │
│  • Automatic invalidation on permission change              │
│  • Django cache framework                                   │
│                                                              │
│  Database Optimization:                                      │
│  • Indexes on frequently queried fields                     │
│  • select_related() for foreign keys                        │
│  • prefetch_related() for many-to-many                      │
│  • Query result caching                                     │
│  • Composite indexes for complex queries                    │
│                                                              │
│  Query Optimization:                                         │
│  • Filter at database level                                 │
│  • Avoid N+1 queries                                        │
│  • Use .only() and .defer() when appropriate                │
│  • Aggregate queries for statistics                         │
└─────────────────────────────────────────────────────────────┘
```

## 19. DEPLOYMENT CONSIDERATIONS

```
┌──────────────────────────────────────────────────────────────┐
│                  DEPLOYMENT CHECKLIST                        │
└──────────────────────┬───────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┬──────────────┐
       │               │               │              │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│   Settings  │ │  Database   │ │   Static   │ │  Email   │
└──────┬──────┘ └──────┬──────┘ └─────┬──────┘ └────┬─────┘
       │               │               │             │
       │               │               │             │
       │               │               │             │
┌──────▼───────────────▼───────────────▼─────────────▼────────┐
│  PRODUCTION SETUP                                            │
│                                                              │
│  Settings Configuration:                                     │
│  • DEBUG = False                                            │
│  • ALLOWED_HOSTS configured                                 │
│  • SECRET_KEY from environment                              │
│  • SECURE_SSL_REDIRECT = True                               │
│  • SESSION_COOKIE_SECURE = True                             │
│  • CSRF_COOKIE_SECURE = True                                │
│                                                              │
│  Database:                                                   │
│  • PostgreSQL or MySQL for production                       │
│  • Database backups configured                              │
│  • Connection pooling                                       │
│  • Read replicas for scaling                                │
│                                                              │
│  Static Files:                                               │
│  • collectstatic command run                                │
│  • CDN for static assets                                    │
│  • Media files storage (S3, etc.)                           │
│  • Compression enabled                                      │
│                                                              │
│  Email:                                                      │
│  • SMTP server configured                                   │
│  • Email backend set                                        │
│  • FROM email address                                       │
│  • Email templates tested                                   │
│                                                              │
│  Security:                                                   │
│  • HTTPS enforced                                           │
│  • Security headers configured                              │
│  • Rate limiting implemented                                │
│  • Firewall rules set                                       │
│                                                              │
│  Monitoring:                                                 │
│  • Error logging (Sentry, etc.)                             │
│  • Performance monitoring                                   │
│  • Uptime monitoring                                        │
│  • Database query monitoring                                │
└─────────────────────────────────────────────────────────────┘
```

## 20. FEATURE SUMMARY

```
┌──────────────────────────────────────────────────────────────┐
│                  COMPLETE FEATURE LIST                       │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │
┌──────────────────────▼───────────────────────────────────────┐
│  AUTHENTICATION & USER MANAGEMENT                            │
│  ✓ User registration with validation                        │
│  ✓ Secure login/logout                                      │
│  ✓ Password reset via email (30-min expiry)                 │
│  ✓ Password history (last 3 passwords)                      │
│  ✓ Profile editing with image upload                        │
│  ✓ Email immutability after registration                    │
│  ✓ Strong password validation                               │
│  ✓ Session-based authentication                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ROLE-BASED ACCESS CONTROL (RBAC)                           │
│  ✓ Three-tier role system (Super Admin, Sub-Admin, User)   │
│  ✓ State-based data access control                         │
│  ✓ Permission caching for performance                       │
│  ✓ Role-based dashboard views                              │
│  ✓ Hierarchical permission model                           │
│  ✓ Multi-state access per user                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ADMIN FEATURES                                              │
│  ✓ User management dashboard                                │
│  ✓ Create/Edit/Delete users                                │
│  ✓ Bulk user creation (CSV format)                          │
│  ✓ Toggle user status (Active/Inactive)                     │
│  ✓ Admin password reset                                     │
│  ✓ User statistics and analytics                            │
│  ✓ Pagination (10 users per page)                           │
│  ✓ Real-time status updates (AJAX)                          │
│  ✓ State permission assignment                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  STOCKIST DATA MANAGEMENT                                    │
│  ✓ Stockist dashboard with statistics                       │
│  ✓ Stockist list with pagination                            │
│  ✓ Detailed stockist view                                   │
│  ✓ Product matching data (PDF vs Excel)                     │
│  ✓ Validation status tracking                               │
│  ✓ Mismatch reports                                         │
│  ✓ Comprehensive data table with filters                    │
│  ✓ State-based data filtering                               │
│  ✓ Month/Year filtering                                     │
│  ✓ Division and product search                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  SECURITY FEATURES                                           │
│  ✓ CSRF protection on all forms                             │
│  ✓ PBKDF2 password hashing                                  │
│  ✓ SQL injection protection (Django ORM)                    │
│  ✓ XSS protection (template escaping)                       │
│  ✓ Input validation and sanitization                        │
│  ✓ Session security                                         │
│  ✓ Permission-based access control                          │
│  ✓ Self-action prevention (delete, deactivate)              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  UI/UX FEATURES                                              │
│  ✓ Responsive design (Bootstrap 5)                          │
│  ✓ Real-time updates without page reload                    │
│  ✓ User-friendly error messages                             │
│  ✓ Success/Error notifications                              │
│  ✓ Intuitive navigation                                     │
│  ✓ Professional admin interface                             │
│  ✓ Font Awesome icons                                       │
│  ✓ Clean and modern design                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  DATA MANAGEMENT                                             │
│  ✓ Custom user model with extended fields                  │
│  ✓ State and permission models                              │
│  ✓ Stockist and product models                              │
│  ✓ Product matching validation                              │
│  ✓ Database indexes for performance                         │
│  ✓ Query optimization                                       │
│  ✓ Data integrity constraints                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: User Actions by Role

### Guest (Unauthenticated)
- View home page
- Register new account
- Login
- Request password reset

### Regular User
- View personal dashboard
- Edit profile (name, username, image)
- Change password
- View stockist data (if state access granted)
- Logout

### Sub-Admin
- All Regular User actions
- View all Users (not Sub-Admins or Super Admins)
- Create new Users
- Edit Users
- Toggle User status
- Assign state permissions to Users
- View all active states' data
- Access RBAC management

### Super Admin
- All Sub-Admin actions
- Manage all users (including Sub-Admins)
- Delete users
- Bulk create users
- Admin password reset
- Full system access
- View all stockist data (all states)
- System configuration

---

## System Flow Summary

1. **Entry Point**: User visits website → Home page
2. **Registration**: Fill form → Validate → Create account → Redirect to login
3. **Authentication**: Login → Validate credentials → Create session → Redirect to dashboard
4. **Dashboard**: Role-based view → Access features based on permissions
5. **User Management** (Admin): View users → Create/Edit/Delete → Assign permissions
6. **Data Access**: Request data → Check role → Filter by state → Return results
7. **Profile Management**: Edit profile → Validate → Update → Save
8. **Password Reset**: Request → Email link → Validate token → Set new password
9. **Logout**: End session → Redirect to login

---

**Created**: February 2026  
**System**: Django User Management with RBAC  
**Version**: Production-ready
