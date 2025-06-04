from django.contrib import admin
from .models import CustomUser, UserVerificationCodes
# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display=('email_or_phone',"email","phone","is_superuser")
admin.site.register(CustomUser,CustomUserAdmin)

admin.site.register(UserVerificationCodes)