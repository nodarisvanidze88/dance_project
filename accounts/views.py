from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from .serializers import LoginSerializer, RegistrationSerializer, LogoutSerializer, UserChangeDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from .errorMessageHandler import get_error_message, errorMessages
from .models import CustomUser
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .validators import validate_password, custom_phone_validator, custom_email_validator
from django.db.models import Q
User = get_user_model()

class RegisterView(CreateAPIView):
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = user.tokens()
        return Response({
            "email_or_phone": serializer.data['email_or_phone'],
            "refresh": str(refresh['refresh']),
            "access": str(refresh['access'])
        }, status=status.HTTP_201_CREATED)
    
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_or_phone = serializer.validated_data.get('email_or_phone')
        password = serializer.validated_data['password']

        # Try to find the user by email_or_phone, email, or phone
        user = CustomUser.objects.filter(
            Q(email_or_phone=email_or_phone) | Q(email=email_or_phone) | Q(phone=email_or_phone)
        ).first()

        if user and check_password(password, user.password):
            # If the password matches, generate tokens
            refresh = user.tokens()
            return Response({
                "access": str(refresh['access']),
                "refresh": str(refresh['refresh']),
            }, status=status.HTTP_200_OK)
        
        # If no user is found or password doesn't match, return invalid credentials error
        return Response(get_error_message(errorMessages, "invalidCredentials"), status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer token",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
            }
        )
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)




class UserChangeDetailsViews(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserChangeDetailsSerializer

    def post(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validates using the serializer

        # Extract validated data
        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone')
        password = serializer.validated_data.get('password')

        # Fetch the user from the database
        db_user = CustomUser.objects.get(id=user.id)

        # Update email
        if email:
            email_searched_user = CustomUser.objects.filter(Q(email_or_phone=email) | Q(email=email)).exclude(id=db_user.id).first()
            if email_searched_user:
                return Response(get_error_message(errorMessages,"usedUserDetails"), status=status.HTTP_400_BAD_REQUEST)
            db_user.email = email
            if "@" in db_user.email_or_phone:
                db_user.email_or_phone = email

        # Update phone
        if phone:
            phone_searched_user = CustomUser.objects.filter(Q(email_or_phone=phone) | Q(phone=phone)).exclude(id=db_user.id).first()
            if phone_searched_user:
                return Response(get_error_message(errorMessages,"usedUserDetails"), status=status.HTTP_400_BAD_REQUEST)
            db_user.phone = phone
            if db_user.email_or_phone.startswith("+995"):
                db_user.email_or_phone = phone

        # Update password
        if password:
            db_user.set_password(password)
            db_user.save() 

        db_user.save()
        return Response(get_error_message(errorMessages,"successChanges"))

    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    

   