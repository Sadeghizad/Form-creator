from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Answer
from .serializers import AnswerSerializer
# Create your views here.
class AnswerSubmit(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerSerializer
    def get_query(self):
        question = self.request.query_params.get('question_id', None)
        return Answer.objects.filter(user=self.request.user,question_id=question)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)