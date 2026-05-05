from django.urls import path
from . import views
from . import stockist_views
from . import stockist_data_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('registration/', views.register_view, name='registration'),  # Alternative URL
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Password Reset URLs
    path('password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # Admin-only URLs
    path('create-user/', views.create_user_view, name='create_user'),
    path('bulk-create-users/', views.bulk_create_users_view, name='bulk_create_users'),
    path('toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('edit-user/<int:user_id>/', views.edit_user_view, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('admin-reset-password/<int:user_id>/', views.admin_reset_password_view, name='admin_reset_password'),
    
    # RBAC URLs
    path('rbac/users/', views.RBACUserListView.as_view(), name='rbac-user-list'),
    path('rbac/users/create/', views.RBACUserCreateView.as_view(), name='rbac-user-create'),
    path('rbac/users/<int:pk>/edit/', views.RBACUserUpdateView.as_view(), name='rbac-user-update'),
    
    # Stockist URLs
    path('stockist/dashboard/', stockist_views.stockist_dashboard, name='stockist-dashboard'),
    path('stockist/list/', stockist_views.stockist_list, name='stockist-list'),
    path('stockist/<str:stockist_code>/', stockist_views.stockist_detail, name='stockist-detail'),
    path('stockist/reports/mismatches/', stockist_views.product_mismatch_report, name='product-mismatch-report'),
    
    # Stockist Data Table (New)
    path('stockist/data/table/', stockist_data_views.stockist_data_table, name='stockist-data-table'),
]