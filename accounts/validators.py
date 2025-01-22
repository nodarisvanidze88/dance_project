from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from django.core.validators import RegexValidator, EmailValidator
from .errorMessageHandler import get_error_message, errorMessages
def validate_password(password):
    try:
        django_validate_password(password)
    except DjangoValidationError as e:
        error_messages = e.messages
        translated_errors = []
        for message in error_messages:
            translated_errors.append({
                "ka": translate_error_to_georgian(message),
                "en": message
            })
        # Raise DRF's ValidationError with the translated errors
        raise serializers.ValidationError(translated_errors)

def translate_error_to_georgian(message):
    translations = {
        "This password is too short. It must contain at least 8 characters.": "ეს პაროლი ძალიან მოკლეა. ის უნდა შეიცავდეს მინიმუმ 8 სიმბოლოს.",
        "This password is too common.": "ეს პაროლი ძალიან გავრცელებულია.",
        "This password is entirely numeric.": "ეს პაროლი მხოლოდ ციფრებით შედგება.",
        # Add more translations as needed
    }
    return translations.get(message, message)

def custom_email_validator(value):
    email_validator = EmailValidator(message=[get_error_message(errorMessages,"emailValidator")])
    return email_validator(value)

def custom_phone_validator(value):
    phone_validator = RegexValidator(
        regex=r'^\+995\d{9}$',
        message=get_error_message(errorMessages,"phoneValidator")
    )
    return phone_validator(value)

