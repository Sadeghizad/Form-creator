from django.db import models

class AdminReport(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    report_data = models.JSONField()


