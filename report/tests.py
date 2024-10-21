# tests.py
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from report.models import AdminReport
from report.tasks import generate_admin_report
from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch

class AdminReportTest(TestCase):
    def test_generate_admin_report(self):
        # Call the task to generate the report
        generate_admin_report()

        # Verify if an AdminReport instance is created
        self.assertEqual(AdminReport.objects.count(), 1)

        # Check if the timestamp is correct (approximately now)
        report = AdminReport.objects.first()
        self.assertTrue(timezone.now() - report.timestamp < timedelta(minutes=1))

        # Check if report_data contains expected keys
        expected_keys = {"timestamp", "users", "forms", "processes", "questions", "answers", "last24hourchanges", "lastweekhourchanges", "lastmonthhourchanges"}
        self.assertTrue(set(report.report_data.keys()).issuperset(expected_keys))

class UpdateFormStatsViewTest(APITestCase):
    @patch('report.tasks.update_form_stats.delay')
    def test_update_form_stats_view(self, mock_update_form_stats):
        url = reverse('update_form_stats')
        response = self.client.post(url)

        # Check if the view returns a 200 status code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], "Form stats update initiated. Check logs for progress.")

        # Ensure the Celery task was called
        mock_update_form_stats.assert_called_once()
