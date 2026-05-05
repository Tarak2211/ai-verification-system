from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, State, StatePermission, PasswordHistory


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StatePermission)
class StatePermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'state', 'granted_by', 'granted_at')
    list_filter = ('state', 'granted_at')
    search_fields = ('user__username', 'state__name')
    ordering = ('-granted_at',)
    readonly_fields = ('granted_at',)
    autocomplete_fields = ('user', 'state', 'granted_by')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'name', 'role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('name', 'email')}),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'name', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    def get_readonly_fields(self, request, obj=None):
        # Make email readonly after creation to enforce immutability
        if obj:  # editing an existing object
            return self.readonly_fields + ('email',)
        return self.readonly_fields



# ============================================================================
# Stockist and Product Matching Admin
# ============================================================================

from .models import Stockist, Division, Product, StockistProductMatch


@admin.register(Stockist)
class StockistAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'state', 'is_active', 'created_at')
    list_filter = ('state', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'state__name')
    ordering = ('code',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('state',)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'division', 'is_active', 'created_at')
    list_filter = ('division', 'is_active', 'created_at')
    search_fields = ('code', 'name', 'division__name')
    ordering = ('code',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('division',)


@admin.register(StockistProductMatch)
class StockistProductMatchAdmin(admin.ModelAdmin):
    list_display = (
        'stockist', 'month_year', 'row_index', 'validation', 
        'pdf_product_short', 'variance', 'created_at'
    )
    list_filter = (
        'month_year', 'validation', 'match_method', 
        'stockist__state', 'excel_division', 'created_at'
    )
    search_fields = (
        'stockist__code', 'stockist__name', 
        'pdf_product', 'excel_product__name', 'excel_product__code'
    )
    ordering = ('-month_year', 'stockist__code', 'row_index')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('stockist', 'excel_division', 'excel_product')
    
    fieldsets = (
        ('Reference Information', {
            'fields': ('stockist', 'month_year', 'row_index')
        }),
        ('PDF Data', {
            'fields': ('pdf_division', 'pdf_product', 'pdf_closing')
        }),
        ('Excel Data', {
            'fields': ('excel_division', 'excel_product', 'excel_closing')
        }),
        ('Matching Results', {
            'fields': ('match_method', 'validation', 'variance', 'label', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def pdf_product_short(self, obj):
        """Show shortened PDF product name"""
        if len(obj.pdf_product) > 40:
            return obj.pdf_product[:40] + '...'
        return obj.pdf_product
    pdf_product_short.short_description = 'PDF Product'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('stockist', 'stockist__state', 'excel_division', 'excel_product')


# Customize Django Admin Site
from django.conf import settings

admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Django Administration')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Django Admin')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Site Administration')



@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('user', 'password_hash', 'created_at')
    
    def has_add_permission(self, request):
        # Prevent manual addition of password history
        return False
    
    def has_change_permission(self, request, obj=None):
        # Prevent editing of password history
        return False
