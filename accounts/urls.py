from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (LoginView,LogoutView, PasswordResetView, 
                    RegisterView, RequestPasswordRecoveryView, UserChangeDetailsViews, 
                    UserEmailVerificationView, UserDetails, 
                    GoogleAuthView, UserEmailVerificationResendView,
                    UserPhoneVerificationResendView, UserPhoneVerificationView)
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegisterView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user-details/', UserDetails.as_view(), name='user-details'),
    path('change-details/', UserChangeDetailsViews.as_view(), name='change-details'),
    path('verify-email/', UserEmailVerificationView.as_view(), name='verify-email'),
    path('resend-email-verification/', UserEmailVerificationResendView.as_view(), name='resend-email-verification'),
    path('verify-phone/', UserPhoneVerificationView.as_view(), name='verify-phone'),
    path('resend-phone-verification/', UserPhoneVerificationResendView.as_view(), name='resend-phone-verification'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),  # <-- new endpoint\
    path("password-recovery-request/", RequestPasswordRecoveryView.as_view(), name="password-recovery"),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),  # <-- this is commented out because it was not used in the original code
]