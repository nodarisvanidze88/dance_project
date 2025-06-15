from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from google.oauth2 import id_token
from google.auth.transport import requests
from .serializers import LoginSerializer, RegistrationSerializer, LogoutSerializer, UserChangeDetailsSerializer, UserEmailVerificationSerializer, UserDetailsSerializer, GoogleAuthSerializer, UserPhoneVerificationSerializer
from rest_framework.permissions import IsAuthenticated
from .errorMessageHandler import get_error_message, errorMessages
from .models import CustomUser, UserVerificationCodes
from .validators import custom_phone_validator, custom_email_validator
from django.db.models import Q
from django.conf import settings
from dotenv import load_dotenv
import random
import os
User = get_user_model()
load_dotenv()
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
        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')
        login_field = serializer.validated_data.get('choose_main_login_field')
        if not email and not phone and not password:
            return Response(get_error_message(errorMessages,"noChanges"), status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user from the database
        db_user = CustomUser.objects.get(id=user.id)
        user_code = UserVerificationCodes.objects.get(user_id=db_user.id)

        if login_field =="email":
            if not email:
                return Response(get_error_message(errorMessages,"emailRequired"), status=status.HTTP_400_BAD_REQUEST)
            try:
                custom_email_validator(email)
            except:
                return Response(get_error_message(errorMessages, "invalidEmail"), status=status.HTTP_400_BAD_REQUEST)
            email_searched_user = CustomUser.objects.filter(Q(email_or_phone=email) | Q(email=email)).exclude(id=db_user.id).first()
            if email_searched_user:
                return Response(get_error_message(errorMessages,"usedUserDetails"), status=status.HTTP_400_BAD_REQUEST)
            db_user.email_or_phone = email
            if db_user.email and db_user.email != email:
                user_code.email_verified = False
                user_code.code = str(random.randint(100000, 999999))
                user_code.save()
                user_code.send_verification_email(new_user=email)
            if not user_code.email_verified:
                user_code.send_verification_email(new_user=email)
            db_user.email = email

        elif login_field == "phone":
            if not phone:
                return Response(get_error_message(errorMessages,"phoneRequired"), status=status.HTTP_400_BAD_REQUEST)
            try:
                custom_phone_validator(phone)
            except:
                return Response(get_error_message(errorMessages,"invalidPhone"), status=status.HTTP_400_BAD_REQUEST)
            db_user.email_or_phone = phone
            if db_user.phone and db_user.phone != phone:
                user_code.phone_verified = False
                user_code.code = str(random.randint(100000, 999999))
                user_code.save()
                user_code.send_verification_sms(new_user=phone)
            if not user_code.phone_verified:
                user_code.send_verification_sms(new_user=phone)
            db_user.phone = phone
        else:
            return Response(get_error_message(errorMessages,"invalidLoginField"), status=status.HTTP_400_BAD_REQUEST)
        if username:
            db_user.username = username
        if password:
            db_user.set_password(password)
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

class UserEmailVerificationResendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_code = UserVerificationCodes.objects.filter(user_id=user.id).first()
        if user_code:
            try:
                user_code.send_verification_email(new_user=user.email)
            except:
                return Response(get_error_message(errorMessages, "sendEmailImpossible"),
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(get_error_message(errorMessages, "emailSentSuccessfully"), status=status.HTTP_200_OK)

        return Response(get_error_message(errorMessages, "emailOrPhoneRequired"),
                        status=status.HTTP_400_BAD_REQUEST)


class UserPhoneVerificationView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserPhoneVerificationSerializer
    def post(self, request):
        code = request.data.get('code')
        user_code = UserVerificationCodes.objects.filter(code=code).first()
        if user_code:
            user_code.phone_verified = True
            user_code.save()
            return Response(get_error_message(errorMessages,"phoneVerified"))
        return Response(get_error_message(errorMessages,"invalidPhoneCode"), status=status.HTTP_400_BAD_REQUEST)

class UserPhoneVerificationResendView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        user_code = UserVerificationCodes.objects.filter(user_id=user.id).first()
        if user_code:
            try:
                user_code.send_verification_sms(new_user=user.phone)
            except:
                return Response(get_error_message(errorMessages,"emailOrPhoneRequired"), status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(get_error_message(errorMessages,"phoneVerificationCodeRequired"))
        return Response(get_error_message(errorMessages,"emailOrPhoneRequired"), status=status.HTTP_400_BAD_REQUEST)

class UserDetails(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailsSerializer
    def get(self, request):
        user = request.user
        user_phone_email_validation = UserVerificationCodes.objects.filter(user_id=user.id).first()
        result = {
            "email_or_phone": user.email_or_phone,
            "username": user.username,
            "email_verified": None,
            "phone_verified": None,
        }
        if user_phone_email_validation:
            if user.email:
                result["email"] = user.email
                if user_phone_email_validation.email_verified:
                    result["email_verified"] = user_phone_email_validation.email_verified
                else:
                    result["email_verified"] = False
            if user.phone:
                result["phone"] = user.phone                
                if user_phone_email_validation.phone_verified:
                    result["phone_verified"] = user_phone_email_validation.phone_verified
                else:
                    result["phone_verified"] = False
        return Response(result)

class GoogleAuthView(GenericAPIView):
    """
    POST endpoint to exchange a Google ID token for our own JWT tokens.
    """
    serializer_class = GoogleAuthSerializer

    def post(self, request, *args, **kwargs):
        # 1. Validate incoming data (which should contain the 'id_token')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_token_value = serializer.validated_data.get('id_token')
        
        try: 
            # 2. Verify the token using Google's library
            #    You must pass the same 'audience' as your front-end's OAuth 2.0 client ID
            google_info = id_token.verify_oauth2_token(
                id_token_value,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=200 
            )
        except ValueError as e:
            # Token is invalid
            return Response({"detail": "Invalid Google token."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. google_info will contain user details from Google if token is valid
        #    typical fields: 'email', 'email_verified', 'sub' (unique user id from Google), 'name', 'picture', etc.

        google_email = google_info.get('email')

        # You could also check google_info.get('email_verified') if needed.
        
        if not google_email:
            return Response({"detail": "No email found in Google token."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Create or retrieve the user from the DB
        user, created = CustomUser.objects.get_or_create(email_or_phone=google_email, email=google_email)
        
        # If user was newly created, optionally create the verification code entry
        if created:
            user.set_password(os.getenv('SUPERUSER_PASSWORD'))  # Set a random password
            user.save()
            verification_code = str(random.randint(100000, 999999))
            # Create the verification code object
            UserVerificationCodes.objects.create(
                user=user,
                code=verification_code,
                email_verified=True  # Because Google verified the email
            )
            # Possibly you treat Google signups as "verified" by default, or require them to verify again in your system.
        
        # 5. Generate JWT tokens via SimpleJWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # 6. Return tokens
        return Response({
            "refresh": str(refresh),
            "access": access_token,
            "email_or_phone": user.email_or_phone
        }, status=status.HTTP_200_OK)