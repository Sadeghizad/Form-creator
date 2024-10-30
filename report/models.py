from django.db import models
from form.models import Form,Question
from user.models import User
class AdminReport(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    report_data = models.JSONField()

class Report(models.Model):
    timestamp=models.DateTimeField(auto_now=True)
    report=models.JSONField()
    form=models.ForeignKey(Form,on_delete=models.CASCADE)

class UserViewForm(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    form=models.ForeignKey(Form,on_delete=models.CASCADE)
class UserViewQuestion(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)