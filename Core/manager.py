from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where Email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, Email, password, **extra_fields):
        """
        Create and save a user with the given Email and password.
        """
        if not Email:
            raise ValueError(_("The Email must be set"))
        Email = self.normalize_email(Email)
        user = self.model(Email=Email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, Email, password, **extra_fields):
        """
        Create and save a SuperUser with the given Email and Password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(Email, password, **extra_fields)