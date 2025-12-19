
# Create your models here.

from django.contrib.auth.models import Group, Permission

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class AuthorManager(BaseUserManager):

    def create_user(
        self,
        username=None,
        email=None,
        phone=None,
        email_or_phone=None,
        password=None,
        role="role1",
        **extra_fields
    ):
        # Use email_or_phone if given to set username/email/phone
        if email_or_phone:
            if "@" in email_or_phone:
                email = email_or_phone
            elif email_or_phone.replace("+", "").isdigit():
                phone = email_or_phone
            else:
                username = email_or_phone

        if not username and not email and not phone:
            raise ValueError("User must have at least one of: username, email, or phone")

        email_or_phone = email or phone or username

        author = self.model(
            username=username or email_or_phone,
            email=email,
            phone=phone,
            email_or_phone=email_or_phone,
            role=role,
            **extra_fields,
        )

        if password:
            author.set_password(password)
        else:
            author.set_unusable_password()

        author.is_active = True
        author.save(using=self._db)
        return author
   

    def create_superuser(
        self,
        username=None,
        email=None,
        phone=None,
        password=None,
        **extra_fields
    ):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not password:
            raise ValueError("Superuser must have a password")

        return self.create_user(
            username=username,
            email=email,
            phone=phone,
            password=password,
            **extra_fields
        )



class Author(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )


    password = models.CharField(null=False, blank=False)
    confirm_password = models.CharField(null=False, blank=False)

    # Email (OAuth / optional)
    email = models.EmailField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    # Phone number
    phone = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    # Login identifier (email or phone)
    email_or_phone = models.CharField(
        max_length=100,
        unique=True,
        null=False,
        blank=False
    )

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("role1", "Role1"),
        ("role2", "Role2"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="role1"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    groups = models.ManyToManyField(
        Group,
        related_name="fortune_author_set",  # change this from default 'user_set'
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="fortune_author_set",  # change this as well
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )


    objects = AuthorManager()

    USERNAME_FIELD = "email_or_phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email_or_phone

    # Helpers
    @property
    def is_email(self):
        return "@" in self.email_or_phone

    @property
    def is_phone(self):
        return self.email_or_phone.replace("+", "").isdigit()

