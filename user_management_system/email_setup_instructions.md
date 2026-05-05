# Email Setup Instructions for UserHub Pro

## Current Status
The system is currently configured for **development mode**, which means password reset emails are printed to the server console instead of being sent to actual email addresses.

## Quick Solution (Development)
Check the server console/terminal where you ran `python manage.py runserver`. The password reset emails are printed there with the reset links.

## Production Email Setup (Gmail SMTP)

### Step 1: Get Gmail App Password
1. Go to your Google Account settings
2. Enable 2-Factor Authentication if not already enabled
3. Go to "App passwords" section
4. Generate a new app password for "Mail"
5. Copy the 16-character app password

### Step 2: Update Settings
Replace the email configuration in `user_management_system/settings.py`:

```python
# Email Configuration for Password Reset
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your Gmail
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'  # Replace with Gmail App Password
DEFAULT_FROM_EMAIL = 'UserHub Pro <your-email@gmail.com>'
```

### Step 3: Test Email
1. Restart the Django server
2. Try the password reset functionality
3. Check your email inbox

## Alternative Email Providers

### Outlook/Hotmail
```python
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### Yahoo Mail
```python
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### Custom SMTP Server
```python
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587  # or 465 for SSL
EMAIL_USE_TLS = True  # or EMAIL_USE_SSL = True for port 465
```

## Environment Variables (Recommended for Production)
For security, use environment variables:

```python
import os
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

## Testing Email Configuration
Create a test script to verify email setup:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email from UserHub Pro.',
    settings.DEFAULT_FROM_EMAIL,
    ['test@example.com'],
    fail_silently=False,
)
```

## Troubleshooting
- **Gmail**: Make sure 2FA is enabled and you're using an App Password
- **Firewall**: Ensure ports 587/465 are not blocked
- **Authentication**: Check username/password are correct
- **TLS/SSL**: Verify the correct security protocol is used