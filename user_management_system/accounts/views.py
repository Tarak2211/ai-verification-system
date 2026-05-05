from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from .forms import (CustomUserRegistrationForm, CustomLoginForm, UserProfileForm, 
                   AdminUserEditForm, AdminCreateUserForm, PasswordResetRequestForm, 
                   PasswordResetConfirmForm, AdminPasswordResetForm)
from .models import CustomUser


def is_superuser(user):
    """Check if user is a superuser"""
    return user.is_authenticated and user.is_superuser


def is_admin_or_superuser(user):
    """Check if user is a superuser or sub-admin"""
    return user.is_authenticated and (user.is_superuser or user.role == 'SUB_ADMIN')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.name}!')
            return redirect('dashboard')
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Dashboard view - different content for superusers, sub-admins, and regular users"""
    if request.user.is_superuser or request.user.role == 'SUB_ADMIN':
        # SuperAdmin and SubAdmin dashboard with user management
        users = CustomUser.objects.all().prefetch_related('state_permissions__state').order_by('-date_joined')
        
        # Sub-Admin can only see Users, not other Sub-Admins
        if request.user.role == 'SUB_ADMIN':
            users = users.filter(role='USER')
        
        paginator = Paginator(users, 10)  # Show 10 users per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'is_superuser': request.user.is_superuser,
            'is_subadmin': request.user.role == 'SUB_ADMIN',
            'page_obj': page_obj,
            'total_users': users.count(),
            'active_users': users.filter(is_active=True).count(),
            'inactive_users': users.filter(is_active=False).count(),
        }
        return render(request, 'accounts/admin_dashboard.html', context)
    else:
        # Regular user dashboard
        return render(request, 'accounts/user_dashboard.html')


@login_required
def profile_view(request):
    """User profile view and edit"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user, user=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})


@user_passes_test(is_superuser)
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status (SuperAdmin only)"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Only POST method allowed.'
        })
    
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Prevent superuser from deactivating themselves
        if user == request.user:
            message = 'You cannot deactivate your own account.'
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'message': message})
            else:
                messages.error(request, message)
                return redirect('dashboard')
        
        # Toggle the status
        old_status = user.is_active
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        success_message = f'User {user.username} has been {status} successfully.'
        
        # Debug logging
        print(f"User {user.username} status changed from {old_status} to {user.is_active}")
        
        # Return JSON for AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': success_message,
                'new_status': user.is_active,
                'old_status': old_status
            })
        else:
            # Return redirect for form submissions
            messages.success(request, success_message)
            return redirect('dashboard')
        
    except Exception as e:
        error_message = f'Error updating user status: {str(e)}'
        print(f"Error in toggle_user_status: {str(e)}")
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': error_message})
        else:
            messages.error(request, error_message)
            return redirect('dashboard')


@login_required
@user_passes_test(is_admin_or_superuser)
def edit_user_view(request, user_id):
    """Edit user details (SuperAdmin and SubAdmin)"""
    user_to_edit = get_object_or_404(CustomUser, id=user_id)
    
    # Check permissions
    if request.user.role == 'SUB_ADMIN':
        # Sub-Admin can only edit Users, not other Sub-Admins or Super Admins
        if user_to_edit.is_superuser or user_to_edit.role == 'SUB_ADMIN':
            messages.error(request, 'You do not have permission to edit this user.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, request.FILES, instance=user_to_edit, user_id=user_id)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user_to_edit.username} updated successfully!')
            return redirect('dashboard')
    else:
        form = AdminUserEditForm(instance=user_to_edit, user_id=user_id)
    
    return render(request, 'accounts/edit_user.html', {'form': form, 'user_obj': user_to_edit})


@user_passes_test(is_superuser)
def delete_user_view(request, user_id):
    """Delete user (SuperAdmin only)"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent superuser from deleting themselves
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} has been deleted successfully.')
        return redirect('dashboard')
    
    return render(request, 'accounts/delete_user.html', {'user_obj': user})


@login_required
@user_passes_test(is_admin_or_superuser)
def create_user_view(request):
    """Create new user (SuperAdmin and SubAdmin)"""
    if request.method == 'POST':
        form = AdminCreateUserForm(request.POST, current_user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" created successfully!')
            return redirect('dashboard')
    else:
        form = AdminCreateUserForm(current_user=request.user)
    
    return render(request, 'accounts/create_user.html', {'form': form})


@user_passes_test(is_superuser)
def bulk_create_users_view(request):
    """Bulk create multiple users (SuperAdmin only)"""
    if request.method == 'POST':
        users_data = request.POST.get('users_data', '').strip()
        if not users_data:
            messages.error(request, 'Please provide user data.')
            return render(request, 'accounts/bulk_create_users.html')
        
        created_users = []
        errors = []
        
        for line_num, line in enumerate(users_data.split('\n'), 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                # Expected format: username,email,name,password
                parts = [part.strip() for part in line.split(',')]
                if len(parts) != 4:
                    errors.append(f'Line {line_num}: Invalid format. Expected: username,email,name,password')
                    continue
                
                username, email, name, password = parts
                
                # Check if user already exists
                if CustomUser.objects.filter(username=username).exists():
                    errors.append(f'Line {line_num}: Username "{username}" already exists')
                    continue
                    
                if CustomUser.objects.filter(email=email).exists():
                    errors.append(f'Line {line_num}: Email "{email}" already exists')
                    continue
                
                # Create user
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    name=name,
                    password=password
                )
                created_users.append(user.username)
                
            except Exception as e:
                errors.append(f'Line {line_num}: Error creating user - {str(e)}')
        
        if created_users:
            messages.success(request, f'Successfully created {len(created_users)} users: {", ".join(created_users)}')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        
        if created_users and not errors:
            return redirect('dashboard')
    
    return render(request, 'accounts/bulk_create_users.html')

def password_reset_request_view(request):
    """Password reset request view"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                f'/accounts/password-reset-confirm/{uid}/{token}/'
            )
            
            # Send email
            subject = 'Password Reset Request - UserHub Pro'
            message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
                'site_name': 'UserHub Pro'
            })
            
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'Error sending email. Please try again later.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_confirm_view(request, uidb64, token):
    """
    Password reset confirmation view with 30-minute token expiry.
    Saves password to history after successful reset.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST, user=user)
            if form.is_valid():
                password = form.cleaned_data['password2']
                
                # Save the new password
                user.set_password(password)
                user.save()
                
                # Add password to history
                from .models import PasswordHistory
                from django.contrib.auth.hashers import make_password
                PasswordHistory.add_password(user, make_password(password))
                
                messages.success(request, 'Your password has been reset successfully. You can now login.')
                return redirect('login')
        else:
            form = PasswordResetConfirmForm(user=user)
        
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'The password reset link is invalid or has expired. Please request a new password reset.')
        return redirect('password_reset_request')


def home_view(request):
    """Home page with registration option for guests and logged-in users"""
    # Always show the home page, don't redirect authenticated users
    return render(request, 'accounts/home.html')

@user_passes_test(is_superuser)
def password_reset_logs_view(request):
    """View recent password reset requests (SuperAdmin only)"""
    # This is a simple view to help admins see recent reset requests
    # In a production system, you'd want to log these to a database
    return render(request, 'accounts/password_reset_logs.html', {
        'message': 'Password reset emails are currently printed to the server console. Check the terminal where you run "python manage.py runserver" to see the reset links.'
    })
@user_passes_test(is_superuser)
def admin_reset_password_view(request, user_id):
    """
    Admin reset user password (SuperAdmin only).
    Saves password to history after successful reset.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = AdminPasswordResetForm(request.POST, user=user)
        if form.is_valid():
            new_password = form.cleaned_data['confirm_password']
            user.set_password(new_password)
            user.save()
            
            # Add password to history
            from .models import PasswordHistory
            from django.contrib.auth.hashers import make_password
            PasswordHistory.add_password(user, make_password(new_password))
            messages.success(request, f'Password for user {user.username} has been reset successfully.')
            return redirect('dashboard')
    else:
        form = AdminPasswordResetForm(user=user)
    
    return render(request, 'accounts/admin_reset_password.html', {'form': form, 'user_obj': user})



# RBAC Views
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from .decorators import RoleRequiredMixin, UserManagementMixin
from .forms import RBACUserCreationForm, RBACUserUpdateForm


class RBACUserCreateView(RoleRequiredMixin, CreateView):
    """
    View for creating new users with role and state permissions.
    """
    model = CustomUser
    form_class = RBACUserCreationForm
    template_name = 'accounts/rbac_user_form.html'
    success_url = reverse_lazy('rbac-user-list')
    allowed_roles = ['SUPER_ADMIN', 'SUB_ADMIN']
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'User created successfully')
        return super().form_valid(form)


class RBACUserUpdateView(RoleRequiredMixin, UserManagementMixin, UpdateView):
    """
    View for updating existing users.
    """
    model = CustomUser
    form_class = RBACUserUpdateForm
    template_name = 'accounts/rbac_user_form.html'
    success_url = reverse_lazy('rbac-user-list')
    allowed_roles = ['SUPER_ADMIN', 'SUB_ADMIN']
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully')
        return super().form_valid(form)


class RBACUserListView(RoleRequiredMixin, ListView):
    """
    View for listing users based on current user's permissions.
    """
    model = CustomUser
    template_name = 'accounts/rbac_user_list.html'
    context_object_name = 'users'
    allowed_roles = ['SUPER_ADMIN', 'SUB_ADMIN']
    paginate_by = 10
    
    def get_queryset(self):
        queryset = CustomUser.objects.all()
        
        if self.request.user.is_sub_admin():
            # Sub-admins can only see Users
            queryset = queryset.filter(role=CustomUser.Role.USER)
        
        return queryset.select_related().prefetch_related('state_permissions__state').order_by('-date_joined')
