# urls.py
from django.urls import path, include
from .views import AnswerSubmit
from .views import (
    PublicCategoryViewSet,
    ExclusiveCategoryViewSet,
    FormViewSet,
    ProcessViewSet,
    QuestionViewSet,
    OptionViewSet
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'answers', AnswerSubmit, basename='answer-submit')
router.register(r'forms', FormViewSet, basename='form')
router.register(r'processes', ProcessViewSet, basename='processes')
router.register(r'questions', QuestionViewSet, basename='questions')
router.register(r'options', OptionViewSet)
router.register(r'public-categories', PublicCategoryViewSet, basename='public-category')
router.register(r'exclusive-categories', ExclusiveCategoryViewSet, basename='exclusive-category')

urlpatterns = [
    path('', include(router.urls)),
]
