from django.urls import path
from apps.users.views import UserDetailView, Login, LoginOtp, LoginConfirm, LoginWithUsernameAndPassword
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('', UserDetailView.as_view()),
    path('login/', Login.as_view()),
    path('login-otp/', LoginOtp.as_view()),
    path('login-confirm/', LoginConfirm.as_view()),
    path('login-password/', LoginWithUsernameAndPassword.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
