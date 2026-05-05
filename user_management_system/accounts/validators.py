import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class AlphanumericSpecialPasswordValidator:
    """
    Validate that the password contains alphabetic characters and special characters.
    """
    def validate(self, password, user=None):
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError(
                _("Password must contain at least one alphabetic character."),
                code='password_no_letter',
            )
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            raise ValidationError(
                _("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;':\",./<>?)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _("Your password must contain at least one alphabetic character and one special character.")


class MinMaxLengthValidator:
    """
    Validate that the password is between min_length and max_length characters.
    """
    def __init__(self, min_length=8, max_length=128):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d characters long."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
        if len(password) > self.max_length:
            raise ValidationError(
                _("Password must be no more than %(max_length)d characters long."),
                code='password_too_long',
                params={'max_length': self.max_length},
            )

    def get_help_text(self):
        return _(
            "Your password must be between %(min_length)d and %(max_length)d characters long."
            % {'min_length': self.min_length, 'max_length': self.max_length}
        )


class UsernameNotInPasswordValidator:
    """
    Validate that the password does not contain the username.
    """
    def validate(self, password, user=None):
        if user and hasattr(user, 'username'):
            username = user.username.lower()
            if username in password.lower():
                raise ValidationError(
                    _("Password cannot contain your username."),
                    code='password_contains_username',
                )

    def get_help_text(self):
        return _("Your password cannot contain your username.")