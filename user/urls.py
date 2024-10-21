from django.urls import path, include
from django.contrib.auth import views
from rest_framework.routers import DefaultRouter
from .views import CustomLoginView,password_reset_confirm_view,CustomRegisterViewSet

router = DefaultRouter()
router.register(r'registration', CustomRegisterViewSet, basename='registration')


urlpatterns = [
    path('auth/login/', CustomLoginView.as_view(), name='custom_login'),
    path(
        'auth/password/reset/confirm/<str:uidb64>/<str:token>/',
        password_reset_confirm_view,
        name='password_reset_confirm'
    ),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/',    include(router.urls)),
]