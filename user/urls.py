from django.urls import path, include
from django.contrib.auth import views
from rest_framework.routers import DefaultRouter
from .views import CustomLoginView, GenerateQRView, Update2FASettingsView
from .views import password_reset_confirm_view, CustomRegisterViewSet

router = DefaultRouter()
router.register(r"registration", CustomRegisterViewSet, basename="registration")


urlpatterns = [
    path("auth/login/", CustomLoginView.as_view(), name="custom_login"),
    path(
        "auth/password/reset/confirm/<str:uidb64>/<str:token>/",
        password_reset_confirm_view,
        name="password_reset_confirm",
    ),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/", include(router.urls)),
    path(
        "update-2fa-settings/",
        Update2FASettingsView.as_view(),
        name="update_2fa_settings",
    ),
    path("generate-qr/", GenerateQRView.as_view({"get": "list"}), name="generate_qr"),
]
