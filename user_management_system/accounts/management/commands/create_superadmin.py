from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser account'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the superuser',
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Full name for the superuser',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Creating SuperAdmin Account')
        )
        self.stdout.write('=' * 40)

        # Get username
        username = options.get('username')
        if not username:
            while True:
                username = input('Username: ').strip()
                if username:
                    if User.objects.filter(username=username).exists():
                        self.stdout.write(
                            self.style.ERROR(f'Username "{username}" already exists. Please choose another.')
                        )
                        continue
                    break
                else:
                    self.stdout.write(
                        self.style.ERROR('Username cannot be empty.')
                    )

        # Get email
        email = options.get('email')
        if not email:
            while True:
                email = input('Email: ').strip()
                if email:
                    if User.objects.filter(email=email).exists():
                        self.stdout.write(
                            self.style.ERROR(f'Email "{email}" already exists. Please choose another.')
                        )
                        continue
                    break
                else:
                    self.stdout.write(
                        self.style.ERROR('Email cannot be empty.')
                    )

        # Get full name
        name = options.get('name')
        if not name:
            while True:
                name = input('Full Name: ').strip()
                if name:
                    break
                else:
                    self.stdout.write(
                        self.style.ERROR('Full name cannot be empty.')
                    )

        # Get password
        while True:
            password = getpass.getpass('Password: ')
            if not password:
                self.stdout.write(
                    self.style.ERROR('Password cannot be empty.')
                )
                continue
            
            password_confirm = getpass.getpass('Confirm Password: ')
            if password != password_confirm:
                self.stdout.write(
                    self.style.ERROR('Passwords do not match.')
                )
                continue
            
            # Validate password
            try:
                user = User(username=username, email=email, name=name)
                user.set_password(password)
                user.full_clean()
                break
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        self.stdout.write(
                            self.style.ERROR(f'{field}: {error}')
                        )

        try:
            # Create the superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                name=name
            )
            
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(f'SuperAdmin "{username}" created successfully!')
            )
            self.stdout.write(f'Username: {user.username}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Name: {user.name}')
            self.stdout.write(f'User ID: {user.id}')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('You can now login with these credentials.')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )