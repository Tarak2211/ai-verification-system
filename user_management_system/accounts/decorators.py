"""
Authorization decorators and mixins for RBAC.
"""
import logging
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomUser

logger = logging.getLogger('rbac')


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
                logger.warning(
                    'Permission denied: unauthenticated access attempt to %s',
                    view_func.__name__
                )
                raise PermissionDenied("Authentication required")
            
            if request.user.role not in allowed_roles:
                logger.warning(
                    'Permission denied: user=%s, role=%s, action=%s, required_roles=%s',
                    request.user.username,
                    request.user.role,
                    view_func.__name__,
                    ', '.join(allowed_roles),
                    extra={
                        'user_id': request.user.id,
                        'user_role': request.user.role,
                        'required_roles': allowed_roles,
                        'view': view_func.__name__
                    }
                )
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
            logger.warning(
                'Permission denied: user=%s, action=%s, target=%s, user_role=%s, target_role=%s',
                request.user.username,
                'manage_user',
                target_user.username,
                request.user.role,
                target_user.role,
                extra={
                    'user_id': request.user.id,
                    'user_role': request.user.role,
                    'target_user_id': target_user.id,
                    'target_role': target_user.role,
                    'view': view_func.__name__
                }
            )
            raise PermissionDenied(
                "You don't have permission to manage this user"
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper


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
            logger.warning(
                'Permission denied: user=%s, role=%s, action=%s, required_roles=%s',
                request.user.username,
                request.user.role,
                self.__class__.__name__,
                ', '.join(self.allowed_roles),
                extra={
                    'user_id': request.user.id,
                    'user_role': request.user.role,
                    'required_roles': self.allowed_roles,
                    'view': self.__class__.__name__
                }
            )
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
            logger.warning(
                'Permission denied: user=%s, action=%s, target=%s, user_role=%s, target_role=%s',
                self.request.user.username,
                'manage_user',
                obj.username,
                self.request.user.role,
                obj.role,
                extra={
                    'user_id': self.request.user.id,
                    'user_role': self.request.user.role,
                    'target_user_id': obj.id,
                    'target_role': obj.role,
                    'view': self.__class__.__name__
                }
            )
            raise PermissionDenied(
                "You don't have permission to manage this user"
            )
        return obj
