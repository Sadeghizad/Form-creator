from django.db import models
from user.models import User

class Form(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Process(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    linear = models.BooleanField(default=False)
    password = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField() 
    is_private = models.BooleanField(default=False)

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    text = models.TextField()
    type = models.IntegerField(choices=[(1, 'Text'), (2, 'Checkbox'), (3, 'Test')])  # e.g., 'text', 'multiple choice', etc.
    required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField() 


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    order = models.IntegerField(null=True, blank=True)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    select = models.ManyToManyField(Option, max_length=255, blank=True, related_name='select')  # For checkbox 
    option = models.ForeignKey(Option, null=True, blank=True, on_delete=models.SET_NULL, related_name='option')  # For test
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
