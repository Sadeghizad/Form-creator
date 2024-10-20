from django.urls import path
from report.views import UpdateFormStatsView,AdminReportView

urlpatterns = [
    path('update-form-stats/', UpdateFormStatsView.as_view(), name='update_form_stats'),
        path('admin-report/', AdminReportView.as_view(), name='admin_report'),
]
