from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator, EmailValidator
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import validate_email_or_phone
User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(write_only=True, 
                                      required=True)
    email_or_phone = serializers.CharField(
        required=True,
        validators=[validate_email_or_phone]
    )
    class Meta:
        model = User
        fields = ['email_or_phone', 'password','password2']

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        
        if not email_or_phone:
            raise ValidationError("Email or Phone is required.")
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        email_or_phone=validated_data['email_or_phone']
        if "@" in email_or_phone:
            email = email_or_phone
            phone = None
        elif email_or_phone.startswith("+995"):
            phone = email_or_phone
            email = None
        else:
            raise ValidationError("Enter a valid email or phone number.")
        try:
            user = User.objects.create(
                email_or_phone=email_or_phone,
                email=email,
                phone=phone 
            )
            user.set_password(validated_data['password'])
            user.save()
            return user
        except:
            raise serializers.ValidationError("User already exists.")

class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
    )
    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        if not email_or_phone:
            raise serializers.ValidationError("Either email or phone must be provided.")
        return attrs
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()