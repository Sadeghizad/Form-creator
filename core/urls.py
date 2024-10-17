"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from rest_framework.routers import DefaultRouter
from form.views import FormViewSet, ProcessViewSet, QuestionViewSet, OptionViewSet, AnswerViewSet, CategoryViewSet
from user.views import LoginView, SignUpView, UpdateProfileViewSet, ChangePasswordView

router = DefaultRouter()
router.register(r'forms', FormViewSet, basename='form')
router.register(r'processes', ProcessViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'options', OptionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'profile', UpdateProfileViewSet, basename='profile') 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('', include(router.urls)), 
    path('change_password', ChangePasswordView.as_view(), name='auth_change_password'),
]
