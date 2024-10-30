from django.urls import path
from report.views import AdminReportView

urlpatterns = [
    path('admin-report/', AdminReportView.as_view(), name='admin_report'),
]
