from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth import get_user_model

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except Exception as e:
            # Handle case where user no longer exists
            if "CustomUser matching query does not exist" in str(e):
                raise InvalidToken("User no longer exists")
            raise e