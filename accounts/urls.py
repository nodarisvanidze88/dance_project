from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LoginView,LogoutView, RegisterView, UserChangeDetailsViews, UserEmailVerificationView, UserDetails, GoogleAuthView
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegisterView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user-details/', UserDetails.as_view(), name='user-details'),
    path('change-details/', UserChangeDetailsViews.as_view(), name='change-details'),
    path('verify-email/', UserEmailVerificationView.as_view(), name='verify-email'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),  # <-- new endpoint
]