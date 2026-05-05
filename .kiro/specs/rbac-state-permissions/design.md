# Design Document: RBAC State Permissions

## Overview

This design implements a Role-Based Access Control (RBAC) system for a Django application using a hierarchical role structure (Super_Admin, Sub_Admin, User) with state-based data access controls. The implementation leverages Django's built-in permission system, custom model managers for query filtering, and middleware for request-level authorization.

The design follows Django best practices by:
- Extending the existing CustomUser model with role and permission relationships
- Using Django's ORM for permission queries and data filtering
- Implementing custom managers for automatic state-based filtering
- Creating reusable decorators and mixins for view-level authorization

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Django Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Views      │◄─────┤  Decorators  │                     │
│  │  (CBV/FBV)   │      │  & Mixins    │                     │
│  └──────┬───────┘      └──────────────┘                     │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                   │
│  │      Permission Validation Layer      │                   │
│  │  - Role checks                        │                   │
│  │  - State permission checks            │                   │
│  └──────┬───────────────────────────────┘                   │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                   │
│  │         Data Access Layer             │                   │
│  │  - Custom QuerySet Managers           │                   │
│  │  - State-based filtering              │                   │
│  └──────┬───────────────────────────────┘                   │
│         │                                                     │
│         ▼                                                     │
│  ┌──────────────────────────────────────┐                   │
│  │           Models Layer                │                   │
│  │  - CustomUser (with role)             │                   │
│  │  - State                              │                   │
│  │  - StatePermission                    │                   │
│  └───────────────────────────────────────┘                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Request arrives** → View receives request with authenticated user
2. **Authorization check** → Decorator/Mixin validates user role and permissions
3. **Data query** → Custom manager applies state-based filtering if user is a User role
4. **Response** → Filtered data returned to view and rendered

## Components and Interfaces

### 1. Models

#### State Model
Represents geographic regions for access control.

```python
class State(models.Model):
    """
    Represents a geographic state for data access control.
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
```

#### CustomUser Model Extension
Extends existing CustomUser model with role field.

```python
class CustomUser(AbstractUser):
    """
    Extended user model with role-based access control.
    """
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        SUB_ADMIN = 'SUB_ADMIN', 'Sub Admin'
        USER = 'USER', 'User'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    
    # Existing fields preserved
    # ... (email, first_name, last_name, etc.)
    
    def is_super_admin(self):
        return self.is_superuser or self.role == self.Role.SUPER_ADMIN
    
    def is_sub_admin(self):
        return self.role == self.Role.SUB_ADMIN
    
    def is_regular_user(self):
        return self.role == self.Role.USER
    
    def can_manage_user(self, target_user):
        """Check if this user can manage the target user."""
        if self.is_super_admin():
            return True
        if self.is_sub_admin():
            return target_user.is_regular_user()
        return False
    
    def get_accessible_states(self):
        """Return queryset of states this user can access."""
        if self.is_super_admin() or self.is_sub_admin():
            return State.objects.filter(is_active=True)
        return State.objects.filter(
            statepermission__user=self,
            is_active=True
        ).distinct()
```

#### StatePermission Model
Links users to states for access control.

```python
class StatePermission(models.Model):
    """
    Grants a user access to data from a specific state.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='state_permissions'
    )
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name='user_permissions'
    )
    granted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_permissions'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'state']
        indexes = [
            models.Index(fields=['user', 'state']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.state.name}"
```

### 2. Custom QuerySet Managers

#### StateFilteredQuerySet
Automatically filters querysets based on user's state permissions.

```python
class StateFilteredQuerySet(models.QuerySet):
    """
    QuerySet that automatically filters by user's accessible states.
    """
    def for_user(self, user):
        """
        Filter queryset based on user's state permissions.
        
        Args:
            user: CustomUser instance
            
        Returns:
            Filtered queryset
        """
        if user.is_super_admin() or user.is_sub_admin():
            # Full access for admins
            return self
        
        # Filter by user's assigned states
        accessible_states = user.get_accessible_states()
        return self.filter(state__in=accessible_states)


class StateFilteredManager(models.Manager):
    """
    Manager that uses StateFilteredQuerySet.
    """
    def get_queryset(self):
        return StateFilteredQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)
```

Usage example for models with state-based data:

```python
class StateData(models.Model):
    """
    Example model with state-based access control.
    """
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    # ... other fields
    
    objects = StateFilteredManager()
    
    class Meta:
        abstract = True
```

### 3. Permission Validation Layer

#### Decorators for Function-Based Views

```python
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404


def role_required(*allowed_roles):
    """
    Decorator to restrict view access by role.
    
    Usage:
        @role_required('SUPER_ADMIN', 'SUB_ADMIN')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")
            
            if request.user.role not in allowed_roles:
                raise PermissionDenied(
                    f"This action requires one of: {', '.join(allowed_roles)}"
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def can_manage_user_required(view_func):
    """
    Decorator to check if user can manage the target user.
    Expects 'user_id' or 'pk' in URL kwargs.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        target_user_id = kwargs.get('user_id') or kwargs.get('pk')
        target_user = get_object_or_404(CustomUser, pk=target_user_id)
        
        if not request.user.can_manage_user(target_user):
            raise PermissionDenied(
                "You don't have permission to manage this user"
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper
```

#### Mixins for Class-Based Views

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin to restrict CBV access by role.
    
    Usage:
        class MyView(RoleRequiredMixin, View):
            allowed_roles = ['SUPER_ADMIN', 'SUB_ADMIN']
    """
    allowed_roles = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.role in self.allowed_roles:
            raise PermissionDenied(
                f"This action requires one of: {', '.join(self.allowed_roles)}"
            )
        return super().dispatch(request, *args, **kwargs)


class UserManagementMixin:
    """
    Mixin for views that manage users.
    Validates that current user can manage the target user.
    """
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.can_manage_user(obj):
            raise PermissionDenied(
                "You don't have permission to manage this user"
            )
        return obj
```

### 4. Forms

#### UserCreationForm with Role Selection

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm


class RBACUserCreationForm(DjangoUserCreationForm):
    """
    User creation form with role selection and state permissions.
    """
    states = forms.ModelMultipleChoiceField(
        queryset=State.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select states this user can access (only for User role)"
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2']
    
    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        
        # Restrict role choices based on current user
        if current_user:
            if current_user.is_sub_admin():
                # Sub-admins can only create Users
                self.fields['role'].choices = [
                    (CustomUser.Role.USER, 'User')
                ]
            elif current_user.is_super_admin():
                # Super-admins can create Sub-Admins and Users
                self.fields['role'].choices = [
                    (CustomUser.Role.SUB_ADMIN, 'Sub Admin'),
                    (CustomUser.Role.USER, 'User')
                ]
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        states = cleaned_data.get('states')
        
        # Validate role selection
        if self.current_user:
            if self.current_user.is_sub_admin() and role != CustomUser.Role.USER:
                raise forms.ValidationError(
                    "Sub-admins can only create users with User role"
                )
        
        # Validate state permissions
        if role == CustomUser.Role.USER and not states:
            raise forms.ValidationError(
                "Users must be assigned at least one state"
            )
        
        if role in [CustomUser.Role.SUPER_ADMIN, CustomUser.Role.SUB_ADMIN] and states:
            cleaned_data['states'] = []  # Clear states for admin roles
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create state permissions
            states = self.cleaned_data.get('states', [])
            for state in states:
                StatePermission.objects.create(
                    user=user,
                    state=state,
                    granted_by=self.current_user
                )
        return user


class RBACUserUpdateForm(forms.ModelForm):
    """
    User update form with role and state permission management.
    """
    states = forms.ModelMultipleChoiceField(
        queryset=State.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select states this user can access"
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    
    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        
        # Pre-populate states
        if self.instance.pk:
            self.fields['states'].initial = self.instance.get_accessible_states()
        
        # Restrict role choices
        if current_user:
            if current_user.is_sub_admin():
                self.fields['role'].choices = [
                    (CustomUser.Role.USER, 'User')
                ]
                self.fields['role'].disabled = True
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        
        # Validate management permissions
        if self.current_user and not self.current_user.can_manage_user(self.instance):
            raise forms.ValidationError(
                "You don't have permission to edit this user"
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Update state permissions
            states = self.cleaned_data.get('states', [])
            
            # Remove existing permissions
            StatePermission.objects.filter(user=user).delete()
            
            # Create new permissions
            if user.is_regular_user():
                for state in states:
                    StatePermission.objects.create(
                        user=user,
                        state=state,
                        granted_by=self.current_user
                    )
        
        return user
```

### 5. Views

#### User Management Views

```python
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.contrib import messages


class UserCreateView(RoleRequiredMixin, CreateView):
    """
    View for creating new users with role and state permissions.
    """
    model = CustomUser
    form_class = RBACUserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user-list')
    allowed_roles = ['SUPER_ADMIN', 'SUB_ADMIN']
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'User created successfully')
        return super().form_valid(form)


class UserUpdateView(RoleRequiredMixin, UserManagementMixin, UpdateView):
    """
    View for updating existing users.
    """
    model = CustomUser
    form_class = RBACUserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user-list')
    allowed_roles = ['SUPER_ADMIN', 'SUB_ADMIN']
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully')
        return super().form_valid(form)


class UserListView(RoleRequiredMixin, ListView):
    """
    View for listing users based on current user's permissions.
    """
    model = CustomUser
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    allowed_roles = ['SUPER_ADMIN', 'SUB_ADMIN']
    
    def get_queryset(self):
        queryset = CustomUser.objects.all()
        
        if self.request.user.is_sub_admin():
            # Sub-admins can only see Users
            queryset = queryset.filter(role=CustomUser.Role.USER)
        
        return queryset.select_related().prefetch_related('state_permissions__state')
```

## Data Models

### Entity Relationship Diagram

```
┌─────────────────┐
│   CustomUser    │
├─────────────────┤
│ id (PK)         │
│ username        │
│ email           │
│ role            │◄──────────┐
│ is_superuser    │           │
│ ...             │           │
└────────┬────────┘           │
         │                    │
         │ 1                  │
         │                    │
         │ *                  │
         ▼                    │
┌─────────────────┐           │
│StatePermission  │           │
├─────────────────┤           │
│ id (PK)         │           │
│ user_id (FK)    │───────────┘
│ state_id (FK)   │───────┐
│ granted_by (FK) │       │
│ granted_at      │       │
└─────────────────┘       │
                          │
                          │ *
                          │
                          │ 1
                          ▼
                  ┌─────────────────┐
                  │     State       │
                  ├─────────────────┤
                  │ id (PK)         │
                  │ name            │
                  │ code            │
                  │ is_active       │
                  └─────────────────┘
```

### Database Schema

**CustomUser Table** (extends existing)
- `role`: VARCHAR(20), choices: SUPER_ADMIN, SUB_ADMIN, USER

**State Table**
- `id`: Primary Key
- `name`: VARCHAR(100), UNIQUE
- `code`: VARCHAR(10), UNIQUE
- `is_active`: BOOLEAN
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

**StatePermission Table**
- `id`: Primary Key
- `user_id`: Foreign Key → CustomUser
- `state_id`: Foreign Key → State
- `granted_by_id`: Foreign Key → CustomUser (nullable)
- `granted_at`: TIMESTAMP
- UNIQUE constraint on (user_id, state_id)
- INDEX on (user_id, state_id)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property Reflection

After analyzing all acceptance criteria, the following redundancies were identified:

- **1.4 is redundant with 1.3**: Querying a user and getting the role is implied by persistence
- **2.4 is redundant with 1.3**: Form submission saving role is covered by persistence property
- **5.2 is redundant with 5.1**: Not applying filtering is the same as returning all data
- **7.4 is redundant with 6.4**: Both test the same edge case of Users with no state assignments

These redundant criteria will not have separate properties.

### Properties

Property 1: Role persistence round-trip
*For any* user account with an assigned role, saving the user to the database and then retrieving it should return the same role value.
**Validates: Requirements 1.2, 1.3**

Property 2: Form role choices for Super_Admin
*For any* Super_Admin user, the user creation form should present exactly Sub_Admin and User as role choices (not Super_Admin).
**Validates: Requirements 3.1**

Property 3: Form role choices for Sub_Admin
*For any* Sub_Admin user, the user creation form should present only User as a role choice.
**Validates: Requirements 4.1**

Property 4: Role validation in forms
*For any* form submission with a role selection, the form validation should check whether the current user has permission to assign that role.
**Validates: Requirements 2.3**

Property 5: Sub_Admin cannot create Sub_Admin
*For any* Sub_Admin user attempting to create a user with Sub_Admin role, the form validation should fail with a descriptive error.
**Validates: Requirements 3.2**

Property 6: User role cannot create users
*For any* User role attempting to access user creation functionality, the system should reject the operation with a permission error.
**Validates: Requirements 3.3**

Property 7: Sub_Admin cannot edit Sub_Admin
*For any* Sub_Admin user attempting to edit another Sub_Admin account, the system should reject the operation with a permission error.
**Validates: Requirements 4.3**

Property 8: Sub_Admin cannot edit Super_Admin
*For any* Sub_Admin user attempting to edit a Super_Admin account, the system should reject the operation with a permission error.
**Validates: Requirements 4.4**

Property 9: Sub_Admin can edit User
*For any* Sub_Admin user attempting to edit a User account, the system should allow the operation to succeed.
**Validates: Requirements 4.2**

Property 10: Super_Admin has unrestricted data access
*For any* Super_Admin user and any data query, the system should return all data without applying state-based filtering.
**Validates: Requirements 3.4**

Property 11: Sub_Admin has unrestricted data access
*For any* Sub_Admin user and any data query, the system should return all data without applying state-based filtering.
**Validates: Requirements 5.1**

Property 12: Sub_Admin sees all Users in list
*For any* Sub_Admin user querying the user list, the system should return all User role accounts regardless of their state assignments.
**Validates: Requirements 5.3**

Property 13: State permission persistence
*For any* User account with assigned state permissions, saving the permissions and then retrieving them should return the same set of states.
**Validates: Requirements 6.2**

Property 14: Multiple state assignment
*For any* User account and any set of one or more states, the system should allow assignment of all states to that user.
**Validates: Requirements 6.3**

Property 15: User with no states has no data access
*For any* User account with zero state permissions, any data query should return an empty result set.
**Validates: Requirements 6.4**

Property 16: User data filtering by assigned states
*For any* User account with state permissions and any data query, the returned results should only include data from the user's assigned states.
**Validates: Requirements 7.1**

Property 17: User cannot access non-assigned state data
*For any* User account and any state not in their assigned states, attempting to query data from that state should return an empty result.
**Validates: Requirements 7.2**

Property 18: User with multiple states sees combined data
*For any* User account assigned to multiple states, data queries should return data from all assigned states (union of results).
**Validates: Requirements 7.3**

Property 19: CRUD operations validate against role
*For any* user and any create, read, update, or delete operation, the system should perform role-based validation before executing the operation.
**Validates: Requirements 8.1**

Property 20: Failed validation returns error
*For any* operation that fails role validation, the system should reject the operation and return a descriptive error message.
**Validates: Requirements 8.2**

Property 21: Permission failures are logged
*For any* permission validation failure, the system should create a log entry with details of the failed operation.
**Validates: Requirements 8.3**

Property 22: Permission changes apply immediately
*For any* user whose role or state permissions are modified, the next request from that user should reflect the updated permissions.
**Validates: Requirements 8.4**

Property 23: Authentication compatibility
*For any* existing user account, the authentication process should continue to work correctly after the RBAC system is added.
**Validates: Requirements 9.2**

Property 24: New states available for assignment
*For any* newly created state in the database, the state should immediately appear in the permission assignment interface.
**Validates: Requirements 10.2**

Property 25: Invalid state references rejected
*For any* permission assignment attempt with a non-existent state reference, the system should reject the assignment with a validation error.
**Validates: Requirements 10.3**

Property 26: State filtering uses unique identifiers
*For any* data query with state filtering, the system should use the state's unique identifier (primary key) for filtering operations.
**Validates: Requirements 10.4**

## Error Handling

### Error Categories

1. **Permission Errors**
   - User lacks required role for operation
   - User attempting to manage higher-privilege accounts
   - User attempting to access non-assigned state data

2. **Validation Errors**
   - Invalid role selection for current user's privilege level
   - User role without state assignments
   - Invalid state references in permissions

3. **Data Integrity Errors**
   - Duplicate state permissions
   - Orphaned permissions (user or state deleted)
   - Invalid role values

### Error Handling Strategy

**Permission Errors:**
```python
from django.core.exceptions import PermissionDenied

# Raise PermissionDenied with descriptive message
raise PermissionDenied("Sub-admins cannot edit other sub-admin accounts")
```

**Validation Errors:**
```python
from django.core.exceptions import ValidationError

# In model clean() method or form validation
raise ValidationError({
    'role': 'Sub-admins can only create users with User role',
    'states': 'Users must be assigned at least one state'
})
```

**Data Integrity:**
- Use database constraints (UNIQUE, FOREIGN KEY)
- Use Django's `on_delete` options appropriately
- Implement model `clean()` methods for complex validation

### Error Response Format

**API/AJAX Responses:**
```json
{
    "success": false,
    "error": {
        "code": "PERMISSION_DENIED",
        "message": "You don't have permission to perform this action",
        "details": {
            "required_role": ["SUPER_ADMIN", "SUB_ADMIN"],
            "current_role": "USER"
        }
    }
}
```

**Form Errors:**
- Use Django's form error system
- Display field-specific errors inline
- Display non-field errors at form top

### Logging Strategy

```python
import logging

logger = logging.getLogger('rbac')

# Log permission failures
logger.warning(
    'Permission denied: user=%s, action=%s, target=%s',
    request.user.username,
    'edit_user',
    target_user.username,
    extra={
        'user_id': request.user.id,
        'user_role': request.user.role,
        'target_user_id': target_user.id,
        'target_role': target_user.role
    }
)

# Log successful privilege escalations
logger.info(
    'User role changed: user=%s, old_role=%s, new_role=%s, changed_by=%s',
    user.username,
    old_role,
    new_role,
    request.user.username
)
```

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs using randomized data

Both testing approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across a wide range of inputs.

### Property-Based Testing Configuration

**Library Selection:** Use `hypothesis` for Python/Django property-based testing

**Configuration:**
- Minimum 100 iterations per property test (due to randomization)
- Each property test must include a comment tag referencing the design property
- Tag format: `# Feature: rbac-state-permissions, Property {number}: {property_text}`

**Example Property Test Structure:**
```python
from hypothesis import given, strategies as st
from hypothesis.extra.django import from_model

class TestRBACProperties(TestCase):
    
    @given(user=from_model(CustomUser, role=st.just(CustomUser.Role.USER)))
    def test_property_16_user_data_filtering(self, user):
        """
        Feature: rbac-state-permissions, Property 16: User data filtering by assigned states
        
        For any User account with state permissions and any data query,
        the returned results should only include data from the user's assigned states.
        """
        # Assign random states to user
        states = State.objects.order_by('?')[:2]
        for state in states:
            StatePermission.objects.create(user=user, state=state)
        
        # Query data
        results = StateData.objects.for_user(user)
        
        # Verify all results are from assigned states
        assigned_state_ids = set(states.values_list('id', flat=True))
        result_state_ids = set(results.values_list('state_id', flat=True))
        
        self.assertTrue(result_state_ids.issubset(assigned_state_ids))
```

### Unit Testing Strategy

**Focus Areas:**
- Specific examples demonstrating correct behavior
- Edge cases (empty states, single state, many states)
- Error conditions (invalid roles, missing permissions)
- Integration points (form validation, view authorization)

**Example Unit Test:**
```python
class TestRBACUnitTests(TestCase):
    
    def test_sub_admin_cannot_create_sub_admin(self):
        """Test that Sub_Admin cannot create another Sub_Admin"""
        sub_admin = CustomUser.objects.create_user(
            username='subadmin',
            role=CustomUser.Role.SUB_ADMIN
        )
        
        form = RBACUserCreationForm(
            data={
                'username': 'newuser',
                'role': CustomUser.Role.SUB_ADMIN,
                'password1': 'testpass123',
                'password2': 'testpass123'
            },
            current_user=sub_admin
        )
        
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)
    
    def test_user_with_no_states_sees_no_data(self):
        """Edge case: User with zero state permissions"""
        user = CustomUser.objects.create_user(
            username='testuser',
            role=CustomUser.Role.USER
        )
        
        # No state permissions assigned
        results = StateData.objects.for_user(user)
        
        self.assertEqual(results.count(), 0)
```

### Test Coverage Goals

- **Models**: 100% coverage of custom methods and properties
- **Forms**: 100% coverage of validation logic
- **Views**: 90%+ coverage of authorization and data filtering
- **Managers**: 100% coverage of custom queryset methods
- **Overall**: 85%+ code coverage

### Integration Testing

**Test Scenarios:**
1. Complete user creation workflow (form → validation → save → permissions)
2. User editing workflow with permission changes
3. Data access across different roles
4. Permission inheritance and cascading
5. Django admin integration

### Manual Testing Checklist

- [ ] Super_Admin can create Sub_Admins and Users
- [ ] Sub_Admin can only create Users
- [ ] Sub_Admin cannot edit other Sub_Admins
- [ ] Users see only their assigned state data
- [ ] State permission changes reflect immediately
- [ ] Form validation prevents invalid role assignments
- [ ] Error messages are clear and actionable
- [ ] Django admin works for Super_Admin
- [ ] Existing authentication continues to work

## Implementation Notes

### Migration Strategy

1. **Add Role Field to CustomUser**
   - Add `role` field with default value `USER`
   - Set existing superusers to `SUPER_ADMIN` role
   - Run data migration

2. **Create State and StatePermission Models**
   - Create new models
   - Add indexes for performance

3. **Update Forms and Views**
   - Modify existing user forms to include role and state fields
   - Add authorization mixins to existing views
   - Update templates to show role and state information

4. **Add Custom Managers**
   - Create StateFilteredManager
   - Apply to models with state-based data
   - Update existing queries to use `.for_user(request.user)`

### Performance Considerations

**Database Indexes:**
- Index on `CustomUser.role` for role-based queries
- Composite index on `StatePermission(user_id, state_id)` for permission lookups
- Index on `State.is_active` for active state queries

**Query Optimization:**
- Use `select_related()` for user → role lookups
- Use `prefetch_related()` for user → state_permissions → state
- Cache state permission lookups for frequently accessed users

**Caching Strategy:**
```python
from django.core.cache import cache

def get_user_accessible_states(user):
    """Get user's accessible states with caching"""
    cache_key = f'user_states_{user.id}'
    states = cache.get(cache_key)
    
    if states is None:
        states = list(user.get_accessible_states().values_list('id', flat=True))
        cache.set(cache_key, states, timeout=300)  # 5 minutes
    
    return states

# Invalidate cache when permissions change
def invalidate_user_state_cache(user):
    cache_key = f'user_states_{user.id}'
    cache.delete(cache_key)
```

### Security Considerations

1. **Always validate on server side** - Never trust client-side role checks
2. **Use Django's permission system** - Leverage built-in security features
3. **Log permission failures** - Enable security auditing
4. **Prevent privilege escalation** - Validate role changes carefully
5. **Use parameterized queries** - Prevent SQL injection (Django ORM handles this)
6. **Validate state references** - Ensure states exist before assignment

### Backward Compatibility

- Existing `is_superuser` flag continues to work
- Super_Admin role automatically set for superusers
- Existing authentication and session management unchanged
- Django admin interface remains functional for superusers
- Existing views without RBAC decorators continue to work (add decorators incrementally)

### Future Enhancements

- **Audit Trail**: Track all permission changes with timestamps and actors
- **Temporary Permissions**: Time-limited state access for Users
- **Permission Groups**: Group states into regions for easier management
- **API Endpoints**: RESTful API for role and permission management
- **Advanced Filtering**: Combine state permissions with other criteria (department, project)
- **Permission Delegation**: Allow Sub_Admins to delegate specific permissions
