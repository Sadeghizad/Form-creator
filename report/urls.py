from django.urls import path
from report.views import AdminReportView,UserReport

urlpatterns = [
    path('admin-report/', AdminReportView.as_view(), name='admin_report'),
    path('report/', UserReport.as_view(), name='report')
]
