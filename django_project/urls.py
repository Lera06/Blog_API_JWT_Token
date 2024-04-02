"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from dj_rest_auth.views import PasswordResetConfirmView
from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from accounts.views import GitHubLogin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('posts.urls')),
    # Log in / Log out icons:
    path("api-auth/", include("rest_framework.urls")),
    # Djoser:
    path('api/v1/auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),          # авторизация по токену
    # JTW:
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Dj-rest-auth:
    path("api/v1/dj-rest-auth/", include("dj_rest_auth.urls")),
    # GitHub:
    path("api/v1/dj-rest-auth/github/", GitHubLogin.as_view(), name='github_login'),
    # Confirm email first
    path('api/v1/dj-rest-auth/registration/account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
    # Then registration
    path("api/v1/dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path('dj-rest-auth/account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    path('api/v1/dj-rest-auth/password/reset/confirm/<slug:uid64>/<slug:token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),


]

