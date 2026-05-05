# Password Reset Security Implementation

## Overview
Enhanced password reset system with time-limited tokens and password history tracking.

## Features Implemented

### 1. 30-Minute Token Expiry
- Password reset links expire after 30 minutes (1800 seconds)
- Configured in `settings.py`: `PASSWORD_RESET_TIMEOUT = 1800`
- Django's built-in token generator automatically enforces this timeout
- Users must request a new reset link if the token expires

### 2. Password History Tracking
- New `PasswordHistory` model tracks the last 3 passwords for each user
- Prevents users from reusing any of their last 3 passwords
- Automatically maintains only the 3 most recent passwords

### 3. Password Reuse Prevention
Applied to:
- User-initiated password reset (forgot password flow)
- Admin-initiated password reset
- All password change operations

## Technical Implementation

### Database Model
```python
class PasswordHistory(models.Model):
    user = ForeignKey to CustomUser
    password_hash = CharField (stores hashed password)
    created_at = DateTimeField (auto-generated)
```

### Key Methods
- `PasswordHistory.add_password(user, password_hash)` - Adds new password and maintains last 3
- `PasswordHistory.check_password_reuse(user, new_password)` - Checks if password was used recently

### Form Validation
Both `PasswordResetConfirmForm` and `AdminPasswordResetForm` now include:
- Password strength validation
- Password history check
- Clear error message: "You cannot reuse any of your last 3 passwords"

### Views Updated
1. `password_reset_confirm_view` - Saves password to history after successful reset
2. `admin_reset_password_view` - Saves password to history when admin resets user password

## User Experience

### Password Reset Flow
1. User requests password reset via email
2. Receives email with reset link
3. Link is valid for 30 minutes
4. User sets new password (must be different from last 3)
5. Password is saved to history
6. User can login with new password

### Error Messages
- **Expired Link**: "The password reset link is invalid or has expired. Please request a new password reset."
- **Password Reuse**: "You cannot reuse any of your last 3 passwords. Please choose a different password."

## Security Benefits
1. **Time-Limited Access**: Reduces window for token exploitation
2. **Password Diversity**: Forces users to create unique passwords
3. **Audit Trail**: Password history provides security audit capability
4. **Compliance**: Meets common security policy requirements

## Admin Interface
- Password history visible in Django admin (read-only)
- Cannot be manually added or edited
- Automatically managed by the system

## Migration
- Migration `0007_passwordhistory.py` created and applied
- No data loss or downtime required
- Existing users start with empty password history

## Configuration
To change the token expiry time, edit `settings.py`:
```python
PASSWORD_RESET_TIMEOUT = 1800  # seconds (30 minutes)
```

Common values:
- 15 minutes: 900
- 30 minutes: 1800 (current)
- 1 hour: 3600
- 24 hours: 86400
