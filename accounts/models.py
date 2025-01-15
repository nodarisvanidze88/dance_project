from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email=None,phone=None, password=None):
        if not email and not phone:
            raise ValueError("The Email or Phone field must be set")
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, phone=phone)
        user.set_password(password)
        user.role = 'customer'
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, phone=None, password=None):
        user = self.create_user(email, phone, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.role = 'staff'
        user.save(using=self._db)
        return user
    
class CustomUser(AbstractBaseUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    )
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=13, 
                             unique=True, 
                             blank=True, 
                             null=True,
                             validators=[
                                 RegexValidator(
                                    regex=r'^\+995\d{9}$',
                                    message="Phone number must be entered in the format: '+995XXXXXXXXX'."
                                    )])
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True

