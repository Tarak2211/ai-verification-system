# Implementation Plan: RBAC State Permissions

## Overview

This implementation plan breaks down the RBAC system into incremental steps, starting with data models, then forms and validation, followed by views and authorization, and finally testing. Each task builds on previous work to ensure continuous integration and early validation.

## Tasks

- [x] 1. Create database models and migrations
  - [x] 1.1 Create State model with fields and validation
    - Implement State model with name, code, is_active fields
    - Add Meta class with ordering and string representation
    - _Requirements: 10.1_
  
  - [x] 1.2 Add role field to CustomUser model
    - Add Role choices (SUPER_ADMIN, SUB_ADMIN, USER)
    - Add role field with default USER
    - Add helper methods: is_super_admin(), is_sub_admin(), is_regular_user()
    - Add can_manage_user() method
    - Add get_accessible_states() method
    - _Requirements: 1.1, 1.2_
  
  - [x] 1.3 Create StatePermission model
    - Implement StatePermission with user, state, granted_by foreign keys
    - Add unique_together constraint on (user, state)
    - Add database index on (user_id, state_id)
    - _Requirements: 6.2, 10.3_
  
  - [x] 1.4 Create and run database migrations
    - Generate migrations for all model changes
    - Create data migration to set existing superusers to SUPER_ADMIN role
    - Run migrations
    - _Requirements: 9.1_
  
  - [ ]* 1.5 Write property test for role persistence
    - **Property 1: Role persistence round-trip**
    - **Validates: Requirements 1.2, 1.3**
  
  - [ ]* 1.6 Write property test for state permission persistence
    - **Property 13: State permission persistence**
    - **Validates: Requirements 6.2**

- [x] 2. Implement custom QuerySet managers for state filtering
  - [x] 2.1 Create StateFilteredQuerySet class
    - Implement for_user() method with role-based filtering logic
    - Handle Super_Admin and Sub_Admin (no filtering)
    - Handle User role (filter by assigned states)
    - _Requirements: 7.1, 3.4, 5.1_
  
  - [x] 2.2 Create StateFilteredManager class
    - Override get_queryset() to return StateFilteredQuerySet
    - Add for_user() convenience method
    - _Requirements: 7.1_
  
  - [ ]* 2.3 Write property test for Super_Admin unrestricted access
    - **Property 10: Super_Admin has unrestricted data access**
    - **Validates: Requirements 3.4**
  
  - [ ]* 2.4 Write property test for Sub_Admin unrestricted access
    - **Property 11: Sub_Admin has unrestricted data access**
    - **Validates: Requirements 5.1**
  
  - [ ]* 2.5 Write property test for User data filtering
    - **Property 16: User data filtering by assigned states**
    - **Validates: Requirements 7.1**
  
  - [ ]* 2.6 Write property test for User with no states
    - **Property 15: User with no states has no data access**
    - **Validates: Requirements 6.4**
  
  - [ ]* 2.7 Write property test for User with multiple states
    - **Property 18: User with multiple states sees combined data**
    - **Validates: Requirements 7.3**
  
  - [ ]* 2.8 Write property test for non-assigned state access
    - **Property 17: User cannot access non-assigned state data**
    - **Validates: Requirements 7.2**

- [x] 3. Create authorization decorators and mixins
  - [x] 3.1 Implement role_required decorator for function-based views
    - Accept variable number of allowed roles
    - Check authentication and role membership
    - Raise PermissionDenied with descriptive message
    - _Requirements: 8.1, 8.2_
  
  - [x] 3.2 Implement can_manage_user_required decorator
    - Extract target user from URL kwargs
    - Call can_manage_user() method
    - Raise PermissionDenied if check fails
    - _Requirements: 4.2, 4.3, 4.4_
  
  - [x] 3.3 Implement RoleRequiredMixin for class-based views
    - Add allowed_roles class attribute
    - Override dispatch() to check role
    - _Requirements: 8.1, 8.2_
  
  - [x] 3.4 Implement UserManagementMixin for class-based views
    - Override get_object() to validate management permission
    - Use can_manage_user() method
    - _Requirements: 4.2, 4.3, 4.4_
  
  - [ ]* 3.5 Write property test for CRUD role validation
    - **Property 19: CRUD operations validate against role**
    - **Validates: Requirements 8.1**
  
  - [ ]* 3.6 Write property test for validation error responses
    - **Property 20: Failed validation returns error**
    - **Validates: Requirements 8.2**

- [x] 4. Implement user management forms
  - [x] 4.1 Create RBACUserCreationForm
    - Extend Django's UserCreationForm
    - Add states field with CheckboxSelectMultiple widget
    - Implement __init__ to restrict role choices based on current_user
    - Super_Admin sees Sub_Admin and User choices
    - Sub_Admin sees only User choice
    - _Requirements: 2.1, 3.1, 4.1_
  
  - [x] 4.2 Add validation logic to RBACUserCreationForm
    - Validate role selection against current user's permissions
    - Validate that Users have at least one state assigned
    - Clear states for admin roles
    - _Requirements: 2.3, 3.2, 6.3, 6.4_
  
  - [x] 4.3 Implement save() method in RBACUserCreationForm
    - Save user with role
    - Create StatePermission records for assigned states
    - Set granted_by to current user
    - _Requirements: 6.2_
  
  - [x] 4.4 Create RBACUserUpdateForm
    - Extend ModelForm with role and states fields
    - Pre-populate states from existing permissions
    - Restrict role choices based on current user
    - Disable role field for Sub_Admins
    - _Requirements: 2.2, 4.2_
  
  - [x] 4.5 Add validation and save logic to RBACUserUpdateForm
    - Validate management permissions using can_manage_user()
    - Delete existing StatePermission records
    - Create new StatePermission records for updated states
    - _Requirements: 4.2, 6.2_
  
  - [ ]* 4.6 Write property test for Super_Admin form choices
    - **Property 2: Form role choices for Super_Admin**
    - **Validates: Requirements 3.1**
  
  - [ ]* 4.7 Write property test for Sub_Admin form choices
    - **Property 3: Form role choices for Sub_Admin**
    - **Validates: Requirements 4.1**
  
  - [ ]* 4.8 Write property test for form role validation
    - **Property 4: Role validation in forms**
    - **Validates: Requirements 2.3**
  
  - [ ]* 4.9 Write property test for Sub_Admin cannot create Sub_Admin
    - **Property 5: Sub_Admin cannot create Sub_Admin**
    - **Validates: Requirements 3.2**
  
  - [ ]* 4.10 Write property test for multiple state assignment
    - **Property 14: Multiple state assignment**
    - **Validates: Requirements 6.3**

- [x] 5. Checkpoint - Ensure models, managers, and forms work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement user management views
  - [x] 6.1 Create UserCreateView
    - Use RoleRequiredMixin with allowed_roles=['SUPER_ADMIN', 'SUB_ADMIN']
    - Use RBACUserCreationForm
    - Pass current_user to form via get_form_kwargs()
    - Add success message
    - _Requirements: 3.1, 4.1_
  
  - [x] 6.2 Create UserUpdateView
    - Use RoleRequiredMixin and UserManagementMixin
    - Use RBACUserUpdateForm
    - Pass current_user to form via get_form_kwargs()
    - Add success message
    - _Requirements: 4.2, 4.3, 4.4_
  
  - [x] 6.3 Create UserListView
    - Use RoleRequiredMixin with allowed_roles=['SUPER_ADMIN', 'SUB_ADMIN']
    - Filter queryset: Sub_Admins see only Users
    - Use select_related and prefetch_related for performance
    - _Requirements: 5.3_
  
  - [ ]* 6.4 Write property test for Sub_Admin user list filtering
    - **Property 12: Sub_Admin sees all Users in list**
    - **Validates: Requirements 5.3**
  
  - [ ]* 6.5 Write property test for Sub_Admin can edit User
    - **Property 9: Sub_Admin can edit User**
    - **Validates: Requirements 4.2**
  
  - [ ]* 6.6 Write property test for Sub_Admin cannot edit Sub_Admin
    - **Property 7: Sub_Admin cannot edit Sub_Admin**
    - **Validates: Requirements 4.3**
  
  - [ ]* 6.7 Write property test for Sub_Admin cannot edit Super_Admin
    - **Property 8: Sub_Admin cannot edit Super_Admin**
    - **Validates: Requirements 4.4**
  
  - [ ]* 6.8 Write property test for User cannot create users
    - **Property 6: User role cannot create users**
    - **Validates: Requirements 3.3**

- [x] 7. Add URL patterns and wire views
  - [x] 7.1 Create URL patterns for user management
    - Add path for user-create
    - Add path for user-update with pk parameter
    - Add path for user-list
    - _Requirements: 2.1, 2.2_
  
  - [x] 7.2 Update existing URLs to use RBAC views
    - Replace or extend existing user management URLs
    - Ensure backward compatibility
    - _Requirements: 9.3_

- [x] 8. Create templates for user management
  - [x] 8.1 Create user_form.html template
    - Display role selection field
    - Display states selection (checkboxes)
    - Show/hide states based on role selection (JavaScript)
    - Display validation errors
    - _Requirements: 2.1, 6.1_
  
  - [x] 8.2 Create user_list.html template
    - Display user table with username, email, role, assigned states
    - Add create, edit, delete action buttons
    - Filter actions based on current user's role
    - _Requirements: 5.3_
  
  - [x] 8.3 Update existing templates to show role information
    - Add role badges/labels to user displays
    - Show state assignments for Users
    - _Requirements: 2.2_

- [x] 9. Implement logging for security auditing
  - [x] 9.1 Add logging to permission validation failures
    - Log in decorators and mixins when PermissionDenied is raised
    - Include user, action, target, and role information
    - _Requirements: 8.3_
  
  - [x] 9.2 Add logging for role and permission changes
    - Log when user roles are changed
    - Log when state permissions are added or removed
    - Include who made the change
    - _Requirements: 8.3_
  
  - [ ]* 9.3 Write property test for permission failure logging
    - **Property 21: Permission failures are logged**
    - **Validates: Requirements 8.3**

- [x] 10. Implement permission change propagation
  - [x] 10.1 Add cache invalidation for user permissions
    - Create helper function to invalidate user state cache
    - Call after StatePermission changes
    - Call after role changes
    - _Requirements: 8.4_
  
  - [x] 10.2 Ensure immediate permission application
    - Test that permission changes apply on next request
    - No session or cache staleness
    - _Requirements: 8.4_
  
  - [ ]* 10.3 Write property test for immediate permission changes
    - **Property 22: Permission changes apply immediately**
    - **Validates: Requirements 8.4**

- [x] 11. Add state management functionality
  - [x] 11.1 Create State admin interface
    - Register State model in Django admin
    - Add list display, search, and filters
    - _Requirements: 10.1, 10.2_
  
  - [ ]* 11.2 Write property test for new state availability
    - **Property 24: New states available for assignment**
    - **Validates: Requirements 10.2**
  
  - [ ]* 11.3 Write property test for invalid state rejection
    - **Property 25: Invalid state references rejected**
    - **Validates: Requirements 10.3**
  
  - [ ]* 11.4 Write property test for state ID filtering
    - **Property 26: State filtering uses unique identifiers**
    - **Validates: Requirements 10.4**

- [x] 12. Checkpoint - Ensure all views and templates work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Add backward compatibility and integration
  - [x] 13.1 Ensure Django admin compatibility
    - Test that Super_Admin can access Django admin
    - Verify all admin functionality works
    - _Requirements: 9.4_
  
  - [x] 13.2 Test authentication compatibility
    - Verify existing login/logout works
    - Verify session management unchanged
    - _Requirements: 9.2_
  
  - [ ]* 13.3 Write property test for authentication compatibility
    - **Property 23: Authentication compatibility**
    - **Validates: Requirements 9.2**

- [-] 14. Performance optimization
  - [x] 14.1 Add database indexes
    - Add index on CustomUser.role
    - Verify composite index on StatePermission(user_id, state_id)
    - Add index on State.is_active
    - _Requirements: Performance_
  
  - [x] 14.2 Implement caching for state permissions
    - Create get_user_accessible_states() with caching
    - Set 5-minute cache timeout
    - Integrate cache invalidation with permission changes
    - _Requirements: Performance_

- [ ] 15. Integration testing and final validation
  - [ ]* 15.1 Write integration test for complete user creation workflow
    - Test form display → validation → save → permissions
    - _Requirements: 1.2, 2.1, 6.2_
  
  - [ ]* 15.2 Write integration test for user editing workflow
    - Test form pre-population → validation → save → permission updates
    - _Requirements: 2.2, 4.2, 6.2_
  
  - [ ]* 15.3 Write integration test for data access across roles
    - Test Super_Admin, Sub_Admin, and User data queries
    - _Requirements: 3.4, 5.1, 7.1_

- [x] 16. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- Use `hypothesis` library for property-based testing in Python
- Each property test must include comment tag: `# Feature: rbac-state-permissions, Property {number}: {property_text}`
- Checkpoints ensure incremental validation at key milestones
