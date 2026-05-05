"""
Custom QuerySet managers for state-based data filtering.
"""
from django.db import models


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
