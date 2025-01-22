from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from .serializers import LoginSerializer, RegistrationSerializer, LogoutSerializer
from rest_framework.permissions import IsAuthenticated
from .errorMessageHandler import get_error_message, errorMessages
from .models import CustomUser
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError
from .validators import validate_password
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
        user = authenticate(email_or_phone=email_or_phone, password=password)


        if user:
            refresh = user.tokens()
            return Response({
                "access": str(refresh['access']),
                "refresh": str(refresh['refresh']),
                
            })
        return Response(get_error_message(errorMessages,"invalidCredentials"), status=status.HTTP_401_UNAUTHORIZED)

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
    serializer_class = RegistrationSerializer

    def post(self, request):
        email_validator = EmailValidator(message=[get_error_message(errorMessages,"emailValidator")])
        phone_validator = RegexValidator(
                                regex=r'^\+995\d{9}$',
                                message=get_error_message(errorMessages,"phoneValidator")
                            )
        user = request.user
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')
        password2 = request.data.get('password2')
        if email:
            try:
                email_validator(email)
            except:
                raise ValidationError(get_error_message(errorMessages,"emailValidator"))
        if phone:
            try:
                phone_validator(phone)
            except:
                raise ValidationError(get_error_message(errorMessages,"phoneValidator"))
        if password:
            validate_password(password)
            if password != password2:
                raise ValidationError(get_error_message(errorMessages,"passwordsNotMatch"))
                    
        db_user = CustomUser.objects.get(email_or_phone=user)
        if email and email_validator(db_user.email_or_phone):
            db_user.email = email
            db_user.email_or_phone = email
        if phone and phone_validator(db_user.email_or_phone):
            db_user.phone = phone
            db_user.email_or_phone = phone
        if password:
            db_user.set_password(password)
        db_user.save()
        return Response(get_error_message(errorMessages,"successChanges"))

    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)