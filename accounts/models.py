from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .errorMessageHandler import get_error_message, errorMessages
from .validators import custom_email_validator, custom_phone_validator
import random
import requests
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
        try:
            instance, created = UserVerificationCodes.objects.get_or_create(user=user)
            if created:
                instance.code = str(random.randint(100000, 999999))
                instance.save()
        except Exception as e:
            print(f"❌ Failed to create verification code: {e}")

        if user.email:
            user.send_verification_email()
        if user.phone:
            user.send_verification_sms()

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
    username = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=13,  
                             blank=True, 
                             null=True,
                             validators=[
                                 RegexValidator(
                                     regex=r'^\+995\d{9}$',
                                     message=get_error_message(errorMessages, 'phoneValidator')
                                 )])
    date_joined = models.DateTimeField(auto_now_add=True)
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


    def send_verification_email(self):
        """
        Uses Django's send_mail to email the verification code to the user.
        Make sure your EMAIL_* settings are configured in settings.py.
        """
        if not self.email:
            return  # no email, skip
        
        subject = "Verify your email"
        try:
            user_code = UserVerificationCodes.objects.get(user=self)
        except UserVerificationCodes.DoesNotExist:
            print("❌ Verification code not found for user.")
            return
        message = f"Your verification code is: {user_code.code}"
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # or "no-reply@yourdomain.com"
                [self.email],
                fail_silently=False
            )
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    def send_verification_sms(self):
        """
        Uses Django's send_mail to email the verification code to the user.
        Make sure your EMAIL_* settings are configured in settings.py.
        """
        if not self.phone:
            return
        try:
            user_code = UserVerificationCodes.objects.get(user=self)
        except UserVerificationCodes.DoesNotExist:
            return  # or handle error
        try:
            message = f"Your verification code is: {user_code.code}"
            url = "https://sender.ge/api/send.php"
            payload = {
                "apikey": settings.SENDER_GE_API_KEY,       # ✅ must match Sender.ge API param
                "smsno": "2",                                # 1 = promo, 2 = transactional
                "destination": self.phone[-9:],              # must be 9 digits only (no +995)
                "content": message,
            }

            requests.post(url, data=payload)
        except requests.RequestException as e:
            print(f"Error sending SMS: {e}")
            # Optionally, you can log the error or handle it as needed.

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


class UserVerificationCodes(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.email_or_phone
    
    def send_verification_email(self, new_user=None):
        """
        Uses Django's send_mail to email the verification code to the user.
        Make sure your EMAIL_* settings are configured in settings.py.
        """
        if not self.user.email:
            return  # no email, skip 
        subject = "Verify your email"
        user_code = self.code
        message = f"Your verification code is: {user_code}"
        target_email = new_user if new_user else self.user.email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # or "no-reply@yourdomain.com"
            [target_email],
            fail_silently=False
        )
    def send_verification_sms(self, new_user=None):
        """
        Uses Django's send_mail to email the verification code to the user.
        Make sure your EMAIL_* settings are configured in settings.py.
        """
        if not self.user.phone:
            return
        try:
            user_code = self.code
            message = f"Your verification code is: {user_code}"
            url = "https://sender.ge/api/send.php"
            payload = {
                "apikey": settings.SENDER_GE_API_KEY,       # ✅ must match Sender.ge API param
                "smsno": "2",                                # 1 = promo, 2 = transactional
                "destination": new_user[-9:] if new_user else self.user.phone[-9:],         # must be 9 digits only (no +995)
                "content": message,
            }

            requests.post(url, data=payload)
        except requests.RequestException as e:
            print(f"Error sending SMS: {e}")
            # Optionally, you can log the error or handle it as needed.