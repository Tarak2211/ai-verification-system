from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import CustomUser
import logging

logger = logging.getLogger('rbac')


class CustomUserRegistrationForm(UserCreationForm):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Check if user exists
            try:
                user = CustomUser.objects.get(username=username)
                if not user.is_active:
                    raise ValidationError("Your account has been deactivated. Please contact your Admin for assistance.")
            except CustomUser.DoesNotExist:
                pass  # Let the authenticate function handle this
            
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise ValidationError("Invalid username or password.")

        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    """
    Form for users to edit their own profile.
    Email and password fields are excluded as per requirements.
    """
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'name', 'profile_image')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise ValidationError("A user with this username already exists.")
        return username


class AdminUserEditForm(forms.ModelForm):
    """
    Form for SuperAdmin to edit user details including role and states.
    """
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    # Role selection
    role = forms.ChoiceField(
        choices=[
            ('USER', 'User'),
            ('SUB_ADMIN', 'Admin'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_role'}),
        label='Role',
        help_text='Select user role'
    )
    
    # Multiple states for both User and Admin roles
    states = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_states', 'class': 'state-checkbox'}),
        label='Assign States',
        help_text='Select states for this user'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'name', 'profile_image', 'role', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)
        
        # Import State model here to avoid circular imports
        from .models import State
        self.fields['states'].queryset = State.objects.filter(is_active=True).order_by('name')
        
        # Pre-populate states if editing existing user
        if self.instance.pk:
            self.fields['states'].initial = self.instance.get_accessible_states()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(pk=self.user_id).exists():
            raise ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.user_id).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        states = cleaned_data.get('states')
        
        # Validate that User role has at least one state assigned
        if role == 'USER' and not states:
            raise ValidationError("Users must be assigned to at least one state.")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data.get('role')
        
        if commit:
            user.save()
            
            # Update state permissions
            from .models import StatePermission, State
            states = self.cleaned_data.get('states', [])
            
            # Remove existing permissions
            StatePermission.objects.filter(user=user).delete()
            
            # For Admin role, if no states selected, assign all states
            if user.role == 'SUB_ADMIN' and not states:
                states = State.objects.filter(is_active=True)
            
            # Create new permissions
            for state in states:
                StatePermission.objects.create(
                    user=user,
                    state=state,
                    granted_by=None  # Will be set by view if available
                )
                
                # Log state assignment
                logger.info(
                    'State permission updated: user=%s, state=%s, role=%s',
                    user.username,
                    state.name,
                    user.role
                )
        
        return user


class AdminCreateUserForm(UserCreationForm):
    """
    Form for SuperAdmin to create new users with additional options including role and state selection.
    """
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    # Role selection
    role = forms.ChoiceField(
        choices=[],  # Will be set in __init__ based on current user
        initial='USER',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_role'}),
        label='Role',
        help_text='Select user role'
    )
    
    # Multiple states for both User and Admin roles
    states = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_states', 'class': 'state-checkbox'}),
        label='Assign States',
        help_text='Select states for this user'
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Account is Active'
    )
    is_staff = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Staff Status (can access admin)'
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'name', 'role', 'password1', 'password2', 'is_active', 'is_staff')
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Import State model here to avoid circular imports
        from .models import State
        self.fields['states'].queryset = State.objects.filter(is_active=True).order_by('name')
        
        # Set role choices based on current user
        if self.current_user:
            if self.current_user.is_superuser:
                # Super Admin can create both User and Admin
                self.fields['role'].choices = [
                    ('USER', 'User'),
                    ('SUB_ADMIN', 'Admin'),
                ]
            elif self.current_user.role == 'SUB_ADMIN':
                # Sub-Admin can only create User
                self.fields['role'].choices = [
                    ('USER', 'User'),
                ]
                self.fields['role'].initial = 'USER'
        else:
            # Default to both if no current user (shouldn't happen)
            self.fields['role'].choices = [
                ('USER', 'User'),
                ('SUB_ADMIN', 'Admin'),
            ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        states = cleaned_data.get('states')
        
        # Validate that User role has at least one state assigned
        if role == 'USER' and not states:
            raise ValidationError("Users must be assigned to at least one state.")
        
        # Validate that Sub-Admin cannot create other Sub-Admins
        if self.current_user and self.current_user.role == 'SUB_ADMIN' and role == 'SUB_ADMIN':
            raise ValidationError("Sub-Admins can only create Users, not other Admins.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = self.cleaned_data.get('is_active', True)
        user.is_staff = self.cleaned_data.get('is_staff', False)
        user.role = self.cleaned_data.get('role', 'USER')
        
        if commit:
            user.save()
            
            # Assign state permissions
            from .models import StatePermission, State
            states = self.cleaned_data.get('states', [])
            
            # For Admin role, if no states selected, assign all states
            if user.role == 'SUB_ADMIN' and not states:
                states = State.objects.filter(is_active=True)
            
            # Create state permissions
            for state in states:
                StatePermission.objects.create(
                    user=user,
                    state=state,
                    granted_by=self.current_user
                )
                
                # Log state assignment
                logger.info(
                    'State permission granted: user=%s, state=%s, role=%s',
                    user.username,
                    state.name,
                    user.role
                )
        
        return user
        
        return user


class PasswordResetRequestForm(forms.Form):
    """
    Form for requesting password reset via email.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email address'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise ValidationError("No user found with this email address.")
        return email


class PasswordResetConfirmForm(forms.Form):
    """
    Form for setting new password after email verification.
    Prevents reuse of last 3 passwords.
    """
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("The two password fields didn't match.")
        
        # Validate password against all validators
        if password1 and self.user:
            from django.contrib.auth.password_validation import validate_password
            validate_password(password1, self.user)
            
            # Check password history - prevent reuse of last 3 passwords
            from .models import PasswordHistory
            if PasswordHistory.check_password_reuse(self.user, password1):
                raise ValidationError(
                    "You cannot reuse any of your last 3 passwords. Please choose a different password."
                )
        
        return password2

class AdminPasswordResetForm(forms.Form):
    """
    Form for SuperAdmin to reset a user's password.
    Prevents reuse of last 3 passwords.
    """
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError("The two password fields didn't match.")
        
        # Validate password against all validators
        if new_password and self.user:
            from django.contrib.auth.password_validation import validate_password
            validate_password(new_password, self.user)
            
            # Check password history - prevent reuse of last 3 passwords
            from .models import PasswordHistory
            if PasswordHistory.check_password_reuse(self.user, new_password):
                raise ValidationError(
                    "You cannot reuse any of your last 3 passwords. Please choose a different password."
                )
        
        return confirm_password



class RBACUserCreationForm(UserCreationForm):
    """
    User creation form with role selection and state permissions.
    """
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    role = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Role'
    )
    states = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select states this user can access (only for User role)"
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'name', 'role', 'password1', 'password2']
    
    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        
        # Import State model here to avoid circular imports
        from .models import State
        self.fields['states'].queryset = State.objects.filter(is_active=True)
        
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
        else:
            # Default to all roles if no current user
            self.fields['role'].choices = CustomUser.Role.choices
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        states = cleaned_data.get('states')
        
        # Validate role selection
        if self.current_user:
            if self.current_user.is_sub_admin() and role != CustomUser.Role.USER:
                raise ValidationError(
                    "Sub-admins can only create users with User role"
                )
        
        # Validate state permissions
        if role == CustomUser.Role.USER and not states:
            raise ValidationError(
                "Users must be assigned at least one state"
            )
        
        if role in [CustomUser.Role.SUPER_ADMIN, CustomUser.Role.SUB_ADMIN] and states:
            cleaned_data['states'] = []  # Clear states for admin roles
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data.get('role')
        if commit:
            user.save()
            # Log user creation
            logger.info(
                'User created: username=%s, role=%s, created_by=%s',
                user.username,
                user.role,
                self.current_user.username if self.current_user else 'system',
                extra={
                    'user_id': user.id,
                    'user_role': user.role,
                    'created_by_id': self.current_user.id if self.current_user else None,
                    'action': 'user_created'
                }
            )
            # Create state permissions
            from .models import StatePermission
            states = self.cleaned_data.get('states', [])
            for state in states:
                StatePermission.objects.create(
                    user=user,
                    state=state,
                    granted_by=self.current_user
                )
                # Log state permission grant
                logger.info(
                    'State permission granted: user=%s, state=%s, granted_by=%s',
                    user.username,
                    state.name,
                    self.current_user.username if self.current_user else 'system',
                    extra={
                        'user_id': user.id,
                        'state_id': state.id,
                        'granted_by_id': self.current_user.id if self.current_user else None,
                        'action': 'state_permission_granted'
                    }
                )
        return user


class RBACUserUpdateForm(forms.ModelForm):
    """
    User update form with role and state permission management.
    """
    role = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Role'
    )
    states = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select states this user can access"
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'name', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        
        # Import State model here to avoid circular imports
        from .models import State
        self.fields['states'].queryset = State.objects.filter(is_active=True)
        
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
            elif current_user.is_super_admin():
                self.fields['role'].choices = [
                    (CustomUser.Role.SUB_ADMIN, 'Sub Admin'),
                    (CustomUser.Role.USER, 'User')
                ]
        else:
            self.fields['role'].choices = CustomUser.Role.choices
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate management permissions
        if self.current_user and not self.current_user.can_manage_user(self.instance):
            raise ValidationError(
                "You don't have permission to edit this user"
            )
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Check if role changed
            old_role = CustomUser.objects.get(pk=user.pk).role if user.pk else None
            if old_role and old_role != user.role:
                logger.info(
                    'User role changed: user=%s, old_role=%s, new_role=%s, changed_by=%s',
                    user.username,
                    old_role,
                    user.role,
                    self.current_user.username if self.current_user else 'system',
                    extra={
                        'user_id': user.id,
                        'old_role': old_role,
                        'new_role': user.role,
                        'changed_by_id': self.current_user.id if self.current_user else None,
                        'action': 'role_changed'
                    }
                )
            
            # Update state permissions
            from .models import StatePermission
            states = self.cleaned_data.get('states', [])
            
            # Get old permissions
            old_states = set(StatePermission.objects.filter(user=user).values_list('state_id', flat=True))
            new_states = set(s.id for s in states)
            
            # Remove existing permissions
            StatePermission.objects.filter(user=user).delete()
            
            # Log removed permissions
            removed_states = old_states - new_states
            if removed_states:
                from .models import State
                for state_id in removed_states:
                    state = State.objects.get(pk=state_id)
                    logger.info(
                        'State permission revoked: user=%s, state=%s, revoked_by=%s',
                        user.username,
                        state.name,
                        self.current_user.username if self.current_user else 'system',
                        extra={
                            'user_id': user.id,
                            'state_id': state_id,
                            'revoked_by_id': self.current_user.id if self.current_user else None,
                            'action': 'state_permission_revoked'
                        }
                    )
            
            # Create new permissions
            if user.is_regular_user():
                for state in states:
                    StatePermission.objects.create(
                        user=user,
                        state=state,
                        granted_by=self.current_user
                    )
                    # Log new permissions
                    if state.id not in old_states:
                        logger.info(
                            'State permission granted: user=%s, state=%s, granted_by=%s',
                            user.username,
                            state.name,
                            self.current_user.username if self.current_user else 'system',
                            extra={
                                'user_id': user.id,
                                'state_id': state.id,
                                'granted_by_id': self.current_user.id if self.current_user else None,
                                'action': 'state_permission_granted'
                            }
                        )
        
        return user
