from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from django.core.cache import cache
import os


def user_profile_image_path(instance, filename):
    """Generate file path for user profile images"""
    ext = filename.split('.')[-1]
    filename = f'user_{instance.id}_profile.{ext}'
    return os.path.join('profile_images', filename)


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
        verbose_name = 'State'
        verbose_name_plural = 'States'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Extended user model with role-based access control.
    """
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        SUB_ADMIN = 'SUB_ADMIN', 'Sub Admin'
        USER = 'USER', 'User'
    
    # UserID is auto-incremental (Primary Key) - handled by Django automatically
    username = models.CharField(
        max_length=150, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]+$',
                message='Username can only contain letters, numbers, and underscores.'
            )
        ]
    )
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    profile_image = models.ImageField(
        upload_to=user_profile_image_path,
        null=True,
        blank=True,
        help_text='Upload a profile image (optional)'
    )
    
    # Role field for RBAC
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        help_text='User role for access control'
    )
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']

    class Meta:
        db_table = 'custom_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_active', 'role']),
        ]

    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.username
    
    def get_profile_image_url(self):
        """Get profile image URL or return default"""
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return '/static/images/default-avatar.png'
    
    # RBAC helper methods
    def is_super_admin(self):
        """Check if user is a Super Admin"""
        return self.is_superuser or self.role == self.Role.SUPER_ADMIN
    
    def is_sub_admin(self):
        """Check if user is a Sub Admin"""
        return self.role == self.Role.SUB_ADMIN
    
    def is_regular_user(self):
        """Check if user is a regular User"""
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
        
        # Try to get from cache first
        cache_key = f'user_states_{self.id}'
        cached_states = cache.get(cache_key)
        
        if cached_states is not None:
            return State.objects.filter(id__in=cached_states)
        
        # Query database and cache result
        states = State.objects.filter(
            user_permissions__user=self,
            is_active=True
        ).distinct()
        
        # Cache state IDs for 5 minutes
        state_ids = list(states.values_list('id', flat=True))
        cache.set(cache_key, state_ids, 300)
        
        return states
    
    def invalidate_state_cache(self):
        """Invalidate cached state permissions for this user."""
        cache_key = f'user_states_{self.id}'
        cache.delete(cache_key)



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
        verbose_name = 'State Permission'
        verbose_name_plural = 'State Permissions'
    
    def __str__(self):
        return f"{self.user.username} - {self.state.name}"
    
    def save(self, *args, **kwargs):
        """Override save to invalidate cache."""
        super().save(*args, **kwargs)
        self.user.invalidate_state_cache()
    
    def delete(self, *args, **kwargs):
        """Override delete to invalidate cache."""
        user = self.user
        super().delete(*args, **kwargs)
        user.invalidate_state_cache()


# ============================================================================
# Stockist and Product Matching Models
# ============================================================================

class Stockist(models.Model):
    """Stockist/Distributor information"""
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='stockists')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stockist'
        ordering = ['code']
        indexes = [
            models.Index(fields=['state', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Division(models.Model):
    """Product divisions (AESTHETIC, COSMECEUTICAL, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'division'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Master product catalog"""
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    division = models.ForeignKey(Division, on_delete=models.PROTECT, related_name='products')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product'
        ordering = ['code']
        indexes = [
            models.Index(fields=['division', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class StockistProductMatch(models.Model):
    """Product matching records between PDF and Excel"""
    
    VALIDATION_CHOICES = [
        ('MATCHED', 'Matched'),
        ('QUANTITY_MISMATCH', 'Quantity Mismatch'),
        ('DIVISION_MISMATCH', 'Division Mismatch'),
        ('QUANTITY_AND_DIVISION_MISMATCH', 'Quantity and Division Mismatch'),
        ('PRODUCT_NOT_FOUND', 'Product Not Found'),
    ]
    
    MATCH_METHOD_CHOICES = [
        ('EXACT', 'Exact'),
        ('FUZZY', 'Fuzzy Match'),
    ]
    
    # Reference data
    row_index = models.IntegerField()
    stockist = models.ForeignKey(Stockist, on_delete=models.CASCADE, related_name='product_matches')
    month_year = models.CharField(max_length=20, db_index=True)
    
    # PDF data
    pdf_division = models.CharField(max_length=100, blank=True)
    pdf_product = models.CharField(max_length=200, blank=True)
    pdf_closing = models.IntegerField(default=0)
    
    # Excel data
    excel_division = models.ForeignKey(Division, on_delete=models.PROTECT, null=True, blank=True)
    excel_product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    excel_closing = models.IntegerField(default=0)
    
    # Matching results
    match_method = models.CharField(max_length=20, choices=MATCH_METHOD_CHOICES, blank=True)
    variance = models.IntegerField(default=0)
    validation = models.CharField(max_length=50, choices=VALIDATION_CHOICES, db_index=True)
    label = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stockist_product_match'
        ordering = ['-month_year', 'stockist', 'row_index']
        indexes = [
            models.Index(fields=['stockist', 'month_year']),
            models.Index(fields=['validation', 'month_year']),
            models.Index(fields=['month_year', 'stockist', 'row_index']),
        ]
        unique_together = [['stockist', 'month_year', 'row_index']]
    
    def __str__(self):
        return f"{self.stockist.code} - {self.month_year} - Row {self.row_index}"
    
    @property
    def state(self):
        """Get state from stockist for easy filtering"""
        return self.stockist.state



class PasswordHistory(models.Model):
    """
    Stores password history for users to prevent password reuse.
    Keeps track of the last 3 passwords for each user.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='password_history'
    )
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'password_history'
        ordering = ['-created_at']
        verbose_name = 'Password History'
        verbose_name_plural = 'Password Histories'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def add_password(cls, user, password_hash):
        """Add a new password to history and maintain only last 3"""
        cls.objects.create(user=user, password_hash=password_hash)
        
        # Keep only the last 3 passwords
        old_passwords = cls.objects.filter(user=user)[3:]
        for old_password in old_passwords:
            old_password.delete()
    
    @classmethod
    def check_password_reuse(cls, user, new_password):
        """Check if the new password matches any of the last 3 passwords"""
        from django.contrib.auth.hashers import check_password
        
        recent_passwords = cls.objects.filter(user=user)[:3]
        for password_record in recent_passwords:
            if check_password(new_password, password_record.password_hash):
                return True
        return False
