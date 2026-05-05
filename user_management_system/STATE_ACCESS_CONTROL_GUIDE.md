# 🗺️ State-Based Access Control Guide

## ✅ What's Implemented

Your system now has:
- ✅ **36 Indian States & Union Territories** in the database
- ✅ **State-based access control** for users
- ✅ **Admin full access** to all states
- ✅ **User restricted access** to assigned states only

---

## 📊 Database Structure

### States Table
Contains all 36 Indian states and union territories:

| State Name | Code | Status |
|------------|------|--------|
| Andhra Pradesh | AP | Active |
| Gujarat | GJ | Active |
| Maharashtra | MH | Active |
| Delhi | DL | Active |
| ... | ... | ... |
| (36 total states) | | |

### User-State Mapping
Each user can be assigned to one or multiple states through the `StatePermission` table.

---

## 🎯 Access Control Logic

### 1. **Super Admin** (SUPER_ADMIN)
```
✓ Access: ALL 36 states
✓ Can create: Sub-Admins + Users
✓ Can edit: Everyone
✓ Can view: All data from all states
```

### 2. **Sub-Admin** (SUB_ADMIN)
```
✓ Access: ALL 36 states
✓ Can create: Users only
✓ Can edit: Users only
✓ Can view: All data from all states
```

### 3. **User** (USER)
```
✓ Access: Only assigned states
✗ Cannot create: Anyone
✗ Cannot edit: Anyone
✓ Can view: Only data from assigned states
```

---

## 🧪 Demo Users Created

| Username | Password | Role | Access |
|----------|----------|------|--------|
| demo_admin | admin123 | SUPER_ADMIN | All 36 states |
| demo_subadmin | subadmin123 | SUB_ADMIN | All 36 states |
| gujarat_user | user123 | USER | Gujarat only |
| maharashtra_user | user123 | USER | Maharashtra only |
| multi_state_user | user123 | USER | Delhi, UP, Rajasthan |

---

## 🚀 How to Use

### Step 1: Start Server
```bash
cd user_management_system
python manage.py runserver
```

### Step 2: Login
Open Chrome: http://localhost:8000/accounts/login/

### Step 3: Test Access Control

**As Admin (demo_admin):**
1. Login with `demo_admin` / `admin123`
2. Go to: http://localhost:8000/accounts/rbac/users/
3. You'll see ALL users
4. Create new users and assign any states

**As Gujarat User (gujarat_user):**
1. Login with `gujarat_user` / `user123`
2. This user can only see Gujarat data
3. Cannot access Maharashtra, Delhi, or other state data

**As Multi-State User (multi_state_user):**
1. Login with `multi_state_user` / `user123`
2. This user can see data from Delhi, UP, and Rajasthan
3. Cannot access other states

---

## 💻 How to Implement in Your Views

### Method 1: Manual Filtering

```python
from django.shortcuts import render
from accounts.models import State
from myapp.models import MyData  # Your model with state field

def my_view(request):
    if request.user.is_super_admin() or request.user.is_sub_admin():
        # Admin sees all data
        data = MyData.objects.all()
    else:
        # User sees only their state data
        accessible_states = request.user.get_accessible_states()
        data = MyData.objects.filter(state__in=accessible_states)
    
    return render(request, 'my_template.html', {'data': data})
```

### Method 2: Using StateFilteredManager (Automatic)

**Step 1: Add StateFilteredManager to your model**

```python
from django.db import models
from accounts.models import State
from accounts.managers import StateFilteredManager

class MyData(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    # ... other fields
    
    # Add this line:
    objects = StateFilteredManager()
```

**Step 2: Use in views**

```python
def my_view(request):
    # Automatically filtered by user's accessible states!
    data = MyData.objects.for_user(request.user)
    return render(request, 'my_template.html', {'data': data})
```

---

## 🎨 Example: Complete Implementation

### models.py
```python
from django.db import models
from accounts.models import State
from accounts.managers import StateFilteredManager

class SalesData(models.Model):
    """Example: Sales data by state"""
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    sales_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    
    objects = StateFilteredManager()  # Enable state filtering
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.product_name} - {self.state.name}"
```

### views.py
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SalesData

@login_required
def sales_dashboard(request):
    # Automatically filtered by user's state access
    sales = SalesData.objects.for_user(request.user)
    
    # Calculate totals
    total_sales = sum(sale.sales_amount for sale in sales)
    
    # Get user's accessible states
    accessible_states = request.user.get_accessible_states()
    
    context = {
        'sales': sales,
        'total_sales': total_sales,
        'accessible_states': accessible_states,
        'state_count': accessible_states.count()
    }
    
    return render(request, 'sales_dashboard.html', context)
```

### template.html
```html
{% extends 'base.html' %}

{% block content %}
<div class="container">
    <h2>Sales Dashboard</h2>
    
    <!-- Show user's access level -->
    <div class="alert alert-info">
        {% if user.is_super_admin or user.is_sub_admin %}
            <strong>Admin Access:</strong> Viewing data from all {{ state_count }} states
        {% else %}
            <strong>Your Access:</strong> Viewing data from {{ state_count }} state(s):
            {% for state in accessible_states %}
                <span class="badge bg-primary">{{ state.name }}</span>
            {% endfor %}
        {% endif %}
    </div>
    
    <!-- Display sales data -->
    <table class="table">
        <thead>
            <tr>
                <th>Product</th>
                <th>State</th>
                <th>Amount</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            {% for sale in sales %}
            <tr>
                <td>{{ sale.product_name }}</td>
                <td>{{ sale.state.name }}</td>
                <td>₹{{ sale.sales_amount }}</td>
                <td>{{ sale.date }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="alert alert-success">
        <strong>Total Sales:</strong> ₹{{ total_sales }}
    </div>
</div>
{% endblock %}
```

---

## 🔐 Security Features

✅ **Automatic Filtering**: Users can only see their assigned state data  
✅ **Database Level**: Filtering happens at query level  
✅ **Caching**: State permissions cached for 5 minutes  
✅ **Logging**: All access attempts logged  
✅ **Validation**: Cannot assign invalid states  

---

## 📝 Managing States

### View All States (Django Admin)
1. Login as admin: http://localhost:8000/admin/
2. Go to: **Accounts → States**
3. You'll see all 36 Indian states

### Add New State
```python
from accounts.models import State

State.objects.create(
    name='New State',
    code='NS',
    is_active=True
)
```

### Assign State to User
```python
from accounts.models import CustomUser, State, StatePermission

user = CustomUser.objects.get(username='someuser')
state = State.objects.get(code='GJ')  # Gujarat

StatePermission.objects.create(
    user=user,
    state=state,
    granted_by=request.user  # Who granted this permission
)
```

### Assign Multiple States
```python
user = CustomUser.objects.get(username='someuser')
state_codes = ['GJ', 'MH', 'DL']  # Gujarat, Maharashtra, Delhi

for code in state_codes:
    state = State.objects.get(code=code)
    StatePermission.objects.create(
        user=user,
        state=state,
        granted_by=request.user
    )
```

---

## 🧪 Testing Access Control

### Test 1: Gujarat User
```bash
# Login as gujarat_user
# Try to access data - should only see Gujarat data
```

### Test 2: Admin
```bash
# Login as demo_admin
# Try to access data - should see ALL state data
```

### Test 3: Multi-State User
```bash
# Login as multi_state_user
# Should see data from Delhi, UP, and Rajasthan only
```

---

## 📊 Quick Reference

### Check User's Accessible States
```python
user = request.user
states = user.get_accessible_states()
print(f"User can access: {states.count()} states")
for state in states:
    print(f"  - {state.name}")
```

### Filter Data by User's States
```python
# Method 1: Manual
accessible_states = request.user.get_accessible_states()
data = MyModel.objects.filter(state__in=accessible_states)

# Method 2: Automatic (if using StateFilteredManager)
data = MyModel.objects.for_user(request.user)
```

### Check if User Can Access Specific State
```python
from accounts.models import State

gujarat = State.objects.get(code='GJ')
accessible_states = request.user.get_accessible_states()

if gujarat in accessible_states:
    print("User can access Gujarat data")
else:
    print("User CANNOT access Gujarat data")
```

---

## ✅ Summary

Your system now has:
- ✅ All 36 Indian states in database
- ✅ State-based access control working
- ✅ Admin sees all states
- ✅ Users see only assigned states
- ✅ Demo users created for testing
- ✅ Easy-to-use filtering methods
- ✅ Secure and cached

**Start testing now:**
```bash
python manage.py runserver
```

Then open: http://localhost:8000/accounts/login/

---

**Need help?** Check the logs at: `logs/rbac.log`
