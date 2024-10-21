# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnswerSubmit

router = DefaultRouter()
router.register(r'answers', AnswerSubmit, basename='answer-submit')

urlpatterns = [
    path('', include(router.urls)),
]
