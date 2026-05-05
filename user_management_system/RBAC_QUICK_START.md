# RBAC System - Quick Start Guide

## 🔗 Important Links

### Application URLs
- **RBAC User Management**: http://localhost:8000/accounts/rbac/users/
- **Create New User**: http://localhost:8000/accounts/rbac/users/create/
- **Login Page**: http://localhost:8000/accounts/login/
- **Dashboard**: http://localhost:8000/dashboard/
- **Django Admin**: http://localhost:8000/admin/

### Admin Interfaces
- **State Management**: http://localhost:8000/admin/accounts/state/
- **State Permissions**: http://localhost:8000/admin/accounts/statepermission/
- **User Management**: http://localhost:8000/admin/accounts/customuser/

---

## 👤 Test Credentials

### Super Admin
- **Username**: `admin`
- **Password**: (your admin password)
- **Access**: Full system access, can create Sub-Admins and Users

### Sub-Admin
- **Username**: `subadmin1`
- **Password**: `test123`
- **Access**: Can create and manage Users only

### Regular User
- **Username**: `user1`
- **Password**: `test123`
- **Access**: Limited to Gujarat state only

---

## 🚀 Quick Start

1. **Start Server**:
   ```bash
   cd user_management_system
   python manage.py runserver
   ```

2. **Access RBAC System**:
   - Open: http://localhost:8000/accounts/rbac/users/
   - Login with admin credentials

3. **Create Users**:
   - Click "Create New User" button
   - Select role and assign states

---

## ✅ Quick Test Checklist

- [ ] Login as Super Admin → http://localhost:8000/accounts/login/
- [ ] Access RBAC User List → http://localhost:8000/accounts/rbac/users/
- [ ] Create a Sub-Admin user
- [ ] Create a User with state permissions
- [ ] Login as Sub-Admin and verify restrictions
- [ ] Check Django Admin → http://localhost:8000/admin/
- [ ] View logs at: `logs/rbac.log`

---

## 📊 Features

✅ 3-tier role system (Super Admin, Sub-Admin, User)  
✅ State-based data access control  
✅ Permission management and validation  
✅ Security logging and auditing  
✅ Performance optimization with caching  
✅ Backward compatible with existing system  

---

## 📞 Support

If you encounter any issues, check:
1. Server is running: http://localhost:8000/
2. You're logged in with correct credentials
3. Log file for errors: `logs/rbac.log`

---

**Last Updated**: February 12, 2026
