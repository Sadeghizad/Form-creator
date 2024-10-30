from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from report.models import AdminReport
from report.tasks import generate_admin_report
from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch
from form.models import Form, Process, Question, Answer, Option
from user.models import User


class AdminReportTest(TestCase):
    def test_generate_admin_report(self):

        generate_admin_report()

        self.assertEqual(AdminReport.objects.count(), 1)

        report = AdminReport.objects.first()
        self.assertTrue(timezone.now() - report.timestamp < timedelta(minutes=1))

        expected_keys = {
            "timestamp",
            "users",
            "forms",
            "processes",
            "questions",
            "answers",
            "last24hourchanges",
            "lastweekhourchanges",
            "lastmonthhourchanges",
        }
        self.assertTrue(set(report.report_data.keys()).issuperset(expected_keys))


class UserReportTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_authenticate(user=self.user)

    def test_generate_user_report(self):
        user = self.user
        form = Form.objects.create(
            user,
            name="testform",
            is_private=False,
            order=[2, 3, 1],
        )
        process1 = Process.objects.create(user=user, order=[2])
        process2 = Process.objects.create(user=user, order=[2, 1])
        process3 = Process.objects.create(user=user, order=[2, 1, 3])
        q1 = Question.objects.create(
            user=user, text="k", type=3, required=False, order=[1, 2, 3]
        )
        q2 = Question.objects.create(
            user=user, text="k", type=2, required=False, order=[1, 2, 3]
        )
        q3 = Question.objects.create(user=user, text="k", type=1, required=False)
        opt1 = Option.objects.create(user=user, text="a")
        opt2 = Option.objects.create(user=user, text="b")
        opt3 = Option.objects.create(user=user, text="c")
        Answer.objects.create(user=user, question=q1, form=form, option=opt1)
        Answer.objects.create(user=user, question=q1, form=form, option=opt2)
        Answer.objects.create(user=user, question=q1, form=form, option=opt3)
        Answer.objects.create(user=user, question=q2, form=form, option=[opt1, opt2])
        Answer.objects.create(user=user, question=q2, form=form, option=[opt3, opt2])
        Answer.objects.create(user=user, question=q3, form=form, text="you are good")
        response = self.client.post("/report/", {"form_id": 1})
