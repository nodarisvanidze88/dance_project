from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from .errorMessageHandler import get_error_message, errorMessages
from .validators import custom_email_validator, custom_phone_validator


def validate_email_or_phone(value):
    try:
        custom_email_validator(value)
    except ValidationError:
        try:
            custom_phone_validator(value)
        except ValidationError:
            raise ValidationError(message=get_error_message(errorMessages,'emailOrPhoneValidator'))

class CustomUserManager(BaseUserManager):
    def create_user(self, email_or_phone=None, password=None):
        if not email_or_phone:
            raise ValueError(get_error_message(errorMessages,'emailOrPhoneValidator'))
        if "@" in email_or_phone:
            email = self.normalize_email(email_or_phone)
            user = self.model(email_or_phone=email, email=email)
        elif email_or_phone.startswith("+995"):
            phone = email_or_phone
            user = self.model(email_or_phone=phone, phone=phone)
        else:
            raise ValueError(get_error_message(errorMessages,'emailOrPhoneValidator'))
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
                                    message=get_error_message(errorMessages,'phoneValidator')
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
        if self.pk:
            old_password = CustomUser.objects.get(pk=self.pk).password
            # Compare old password hash to new password hash
            if self.password != old_password:
                # But also check if self._password is set.
                # If _password is None, it means you didn't call set_password(raw_pw).
                # Without carefully using _password, you can easily re-hash a hash.
                if self._password:
                    # self._password is the raw password
                    self.set_password(self._password)
                # else do nothing
        super().save(*args, **kwargs)