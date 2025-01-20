from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError


def validate_email_or_phone(value):
    email_validator = EmailValidator(message="Enter a valid email address.")
    phone_validator = RegexValidator(
        regex=r'^\+995\d{9}$',
        message="Phone number must be entered in the format: '+995XXXXXXXXX'."
    )
    try:
        email_validator(value)
    except ValidationError:
        try:
            phone_validator(value)
        except ValidationError:
            raise ValidationError("Enter a valid email or phone number.")

class CustomUserManager(BaseUserManager):
    def create_user(self, email_or_phone=None, password=None):
        if not email_or_phone:
            raise ValueError("The Email or Phone field must be set")
        if "@" in email_or_phone:
            email = self.normalize_email(email_or_phone)
            user = self.model(email_or_phone=email, email=email)
        elif email_or_phone.startswith("+995"):
            phone = email_or_phone
            user = self.model(email_or_phone=phone, phone=phone)
        else:
            raise ValueError("Email or Phone is required.")
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email_or_phone=None, password=None):
        user = self.create_user(email_or_phone, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
class CustomUser(AbstractBaseUser):
    email_or_phone = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_email_or_phone]
    )
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=13,  
                             blank=True, 
                             null=True,
                             validators=[
                                 RegexValidator(
                                    regex=r'^\+995\d{9}$',
                                    message="Phone number must be entered in the format: '+995XXXXXXXXX'."
                                    )])
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email_or_phone'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email_or_phone
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True

    def tokens(self):
        refresh=RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    def save(self, *args, **kwargs):
        if not self.pk or not CustomUser.objects.filter(pk=self.pk).exists():
            # New user, password hashing is handled by Django's default creation
            super().save(*args, **kwargs)
        else:
            old_password = CustomUser.objects.get(pk=self.pk).password
            if self.password != old_password:  # Password has been changed
                self.set_password(self.password)
        super().save(*args, **kwargs)