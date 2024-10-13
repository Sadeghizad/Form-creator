from django.db import models
from form.models import Form
from user.models import User

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  


class ReportRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('generated', 'Generated')], default='pending')

