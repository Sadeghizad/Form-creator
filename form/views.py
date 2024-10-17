from django.shortcuts import render
from rest_framework import viewsets, exceptions, status
from .models import Category, Form, Answer, Option, Question, Process
from .serializers import CategorySerializer, AnswerSerializer, OptionSerializer, QuestionSerializer
from .serializers import ProcessSerializer, FormSerializer
from rest_framework import permissions  
from rest_framework.permissions import IsAuthenticated
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.urls import reverse
from rest_framework.response import Response

class IsOwner(permissions.BasePermission):
    """
    Custom permission to allow only the creator of a form to create, update, or delete its processes/questions,
    and ensure that only authenticated users can answer questions.
    """
    message = "You do not have permission to perform this action."

    def has_object_permission(self, request, view, obj):
       
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == 'POST':
            return True    
        
        
        if hasattr(obj, 'form'):  # For processes
            form = obj.form
        elif hasattr(obj, 'process'):  # For questions
            form = obj.process.form
        else:
            form = obj

      
        if request.method in permissions.SAFE_METHODS:
            return True
        
       
        return form.user == request.user

    def has_permission(self, request, view):
       
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return True      
        return request.user.is_authenticated    

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    permission_classes = [IsOwner]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsOwner]

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context() 
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)    

class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [IsOwner]
    

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()  
        return super().get_serializer(*args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        process = self.get_object()

     
        if process.is_private:
        
            password = request.query_params.get('password') or request.data.get('password')

            if not password:
                raise exceptions.PermissionDenied("This process is private. Please provide a password.")
            
       
            if process.password != password:
                raise exceptions.PermissionDenied("Incorrect password. Access denied.")

        return super().retrieve(request, *args, **kwargs) 

    def perform_create(self, serializer):
       
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsOwner] 
 

    def retrieve(self, request, *args, **kwargs):
        form = self.get_object()
        if form.is_private:
            password = request.query_params.get('password') or request.data.get('password')
            if not password:
                raise exceptions.PermissionDenied("This form is private. Please provide a password.")
        
            if form.password != password:
                raise exceptions.PermissionDenied("Incorrect password. Access denied.")

        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        form = serializer.save(user=self.request.user)
        form.url = self.request.build_absolute_uri(reverse('form-detail', args=[form.id]))
        form.save()


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.select_related('question__process').all()
    serializer_class = AnswerSerializer
