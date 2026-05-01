from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# TokenObtainPairView = login endpoint (email + password → access + refresh tokens)
# TokenRefreshView = use refresh token to get a new access token

from .views import RegisterView, MeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]