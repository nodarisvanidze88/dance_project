from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from .validators import validate_password
from .models import validate_email_or_phone
from .errorMessageHandler import errorMessages, get_error_message
User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
    )
    email_or_phone = serializers.CharField(
        required=True,
        validators=[validate_email_or_phone]
    )
    class Meta:
        model = User
        fields = ['email_or_phone', 'password','password2']

    def to_internal_value(self, data):
        """
        Override to ensure multilingual error formatting.
        """
        try:
            return super().to_internal_value(data)
        except ValidationError as exc:
            detail = exc.detail
            for field, messages in detail.items():
                if isinstance(messages, list) and isinstance(messages[0], dict):
                    detail[field] = messages  
                else:
                    detail[field] = [get_error_message(errorMessages, "emailOrPhoneValidator")]
            raise ValidationError(detail)
        
    def run_validation(self, data):
        """
        Override to provide multilingual required field error messages.
        """
        if not data:
            errors = {
                "email_or_phone": [
                    get_error_message(errorMessages, "emailOrPhoneRequired")
                ],
                "password": [
                    get_error_message(errorMessages, "passwordRequired")
                ],
                "password2": [
                    get_error_message(errorMessages, "passwordRequired")
                ],
            }
            raise ValidationError(errors)
        return super().run_validation(data)
    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        
        if not email_or_phone:
            raise ValidationError(get_error_message(errorMessages,"emailOrPhoneRequired"))
        if attrs['password'] != attrs['password2']:
            raise ValidationError({"password": get_error_message(errorMessages, "passwordsNotMatch")})
        return attrs
    
    def create(self, validated_data):
        email_or_phone=validated_data['email_or_phone']
        password = validated_data['password']
        if "@" in email_or_phone:
            email = email_or_phone
            phone = None
        elif email_or_phone.startswith("+995"):
            phone = email_or_phone
            email = None
        else:
            raise ValidationError(get_error_message(errorMessages, "emailOrPhoneValidator"))
        try:
            user = User.objects.create_user(
                email_or_phone=email_or_phone,

                password=password
            )
        except:
            raise ValidationError(get_error_message(errorMessages,"userExcist"))

        return user

class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(
        required=True,
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    def run_validation(self, data):
        """
        Override to provide multilingual required field error messages.
        """
        if not data:
            errors = {
                "email_or_phone": [
                    get_error_message(errorMessages, "emailOrPhoneRequired")
                ],
                "password": [
                    get_error_message(errorMessages, "passwordRequired")
                ],
            }
            raise ValidationError(errors)

        for field, value in data.items():
            if not value.strip():
                if field == "email_or_phone":
                    raise ValidationError({
                        "email_or_phone": [
                            get_error_message(errorMessages, "emailOrPhoneBlank")
                        ]
                    })
                if field == "password":
                    raise ValidationError({
                        "password": [
                            get_error_message(errorMessages, "passwordBlank")
                        ]
                    })

        return super().run_validation(data)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        if not email_or_phone:
            raise serializers.ValidationError({
                "email_or_phone": [
                    get_error_message(errorMessages, "emailOrPhoneRequired")
                ]
            })
        return attrs

    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()