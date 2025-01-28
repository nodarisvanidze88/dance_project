from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from .serializers import LoginSerializer, RegistrationSerializer, LogoutSerializer, UserChangeDetailsSerializer, UserEmailVerificationSerializer, UserDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from .errorMessageHandler import get_error_message, errorMessages
from .models import CustomUser, UserVerificationCodes
from .validators import custom_phone_validator, custom_email_validator
from django.db.models import Q
import random
User = get_user_model()

class RegisterView(CreateAPIView):
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_code_data = UserVerificationCodes.objects.filter(user_id=request.data.get('user_id')).first()
        refresh = user.tokens()
        result = {
            "email_or_phone": serializer.data['email_or_phone'],
            "refresh": str(refresh['refresh']),
            "access": str(refresh['access'])
        }
        if user_code_data:
            try:
                custom_email_validator(serializer.data['email_or_phone'])
            except:
                pass
            else:
                result["email_verified"] = user_code_data.email_verified
            try:
                custom_phone_validator(serializer.data['email_or_phone'])
            except:
                pass
            else:
                result["phone_verified"] = user_code_data.phone_verified
        return Response(result, status=status.HTTP_201_CREATED)
    
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
        user_code = UserVerificationCodes.objects.get(user_id=db_user.id)
        print(user_code.code)

        # Update email
        if email:
            email_searched_user = CustomUser.objects.filter(Q(email_or_phone=email) | Q(email=email)).exclude(id=db_user.id).first()
            if email_searched_user:
                return Response(get_error_message(errorMessages,"usedUserDetails"), status=status.HTTP_400_BAD_REQUEST)
            if "@" in db_user.email_or_phone:
                db_user.email_or_phone = email
                if db_user.email and db_user.email != email:
                    user_code.email_verified = False
                    user_code.code = str(random.randint(100000, 999999))
                    user_code.save()
                    user_code.send_verification_email(new_user=email)
            db_user.email = email

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
    
class UserEmailVerificationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserEmailVerificationSerializer
    def post(self, request):
        code = request.data.get('code')
        user_code = UserVerificationCodes.objects.filter(code=code).first()
        if user_code:
            user_code.email_verified = True
            user_code.save()
            return Response(get_error_message(errorMessages,"emailVerified"))
        return Response(get_error_message(errorMessages,"invalidEmailCode"), status=status.HTTP_400_BAD_REQUEST)
    
class UserDetails(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailsSerializer
    def get(self, request):
        user = request.user
        user_phone_email_validation = UserVerificationCodes.objects.filter(user_id=user.id).first()
        result = {
            "email_or_phone": user.email_or_phone,
        }
        if user.email:
            result["email"] = user.email
        if user.phone:
            result["phone"] = user.phone
        if user_phone_email_validation:
            if user_phone_email_validation.email_verified:
                result["email_verified"] = user_phone_email_validation.email_verified
            if user_phone_email_validation.phone_verified:
                result["phone_verified"] = user_phone_email_validation.phone_verified
        return Response(result)
   