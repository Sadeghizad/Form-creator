from rest_framework import viewsets, exceptions, status
from .models import Category, Form, Answer, Option, Question, Process
from .serializers import (
    CategorySerializer,
    AnswerSerializer,
    OptionSerializer,
    QuestionSerializer,
)
from .serializers import ProcessSerializer, FormSerializer
from rest_framework import permissions
from django.urls import reverse
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.core.exceptions import PermissionDenied
from report.models import Report

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    Authenticated users can create (POST).
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        
        return True  

    def has_object_permission(self, request, view, obj):

        return obj.user == request.user



class IsAdmin(permissions.BasePermission):
    message = "Only admins can create public categories."

    def has_permission(self, request, view):
        if (
            request.user.role == "admin" or request.user.is_staff
        ) and request.user.is_authenticated:
            return True
        return False


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [IsOwner]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by("order")
    serializer_class = QuestionSerializer
    permission_classes = [IsOwner]

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)
    # def perform_update(self, serializer):
    #     Report.objects.delete(form=)

class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsOwner]

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        process = self.get_object()

        if process.is_private:

            password = request.query_params.get("password") or request.data.get(
                "password"
            )

            if not password:
                raise exceptions.PermissionDenied(
                    "This process is private. Please provide a password."
                )

            if process.password != password:
                raise exceptions.PermissionDenied("Incorrect password. Access denied.")

        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)


class PublicCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(user__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.role == "admin" or self.request.user.is_staff:
            serializer.save(user=None)
        else:
            raise PermissionDenied("Only admins can create public categories.")


class ExclusiveCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsOwner]

    def retrieve(self, request, *args, **kwargs):
        form = self.get_object()
        if form.is_private:
            password = request.query_params.get("password") or request.data.get(
                "password"
            )
            if not password:
                raise exceptions.PermissionDenied(
                    "This form is private. Please provide a password."
                )

            if form.password != password:
                raise exceptions.PermissionDenied("Incorrect password. Access denied.")

        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        form = serializer.save(user=self.request.user)
        form.url = self.request.build_absolute_uri(
            reverse("form-detail", args=[form.id])
        )
        form.save()


# Create your views here.
class AnswerSubmit(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerSerializer

    def get_queryset(self):
        question = self.request.query_params.get("question_id", None)
        return Answer.objects.filter(user=self.request.user, question_id=question)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
