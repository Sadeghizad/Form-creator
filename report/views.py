from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from report.tasks import generate_admin_report
from .models import Report, UserViewQuestion, UserViewForm, AdminReport
from form.models import Answer, Question
from rest_framework.permissions import IsAdminUser


class AdminReportView(APIView):
    permission_classes = IsAdminUser

    def post(self, request):
        generate_admin_report.delay()

        return Response(
            {"message": "admin report update initiated. Check logs for progress."},
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        return Response(
            AdminReport.objects.latest().report_data, status=status.HTTP_200_OK
        )


class UserReport(APIView):
    def post(self, request):
        formid = request.data.get("form_id")
        try:
            last_report = Report.objects.get(form_id=formid)
            print("last record exist")
        except:
            last_report = None
        report = {}
        if last_report:
            answers = Answer.objects.filter(
                form_id=formid, created_at__gte=last_report.timestamp
            )
            report = last_report.report
            print("last report extracted")
        else:
            answers = Answer.objects.filter(form_id=formid)
            report["form_id"] = formid
            report["views"] = UserViewForm.objects.filter(form_id=formid).count()
            report["questions"] = {}
            questions = {}
            print("new report ready")

        for answer in answers:
            print("answer cycle start")
            question_id = answer.question.id
            q_idstr = str(question_id)
            option_ids = None
            text = answer.text

            if answer.option:
                option_ids = [answer.option.id]
            if answer.select:
                option_ids = list(answer.select.all())

            # Initialize the question entry if it doesn't exist
            if q_idstr not in questions:
                questions[q_idstr] = {"views": 0, "ans": []}  # Initialize views and ans

            questions[q_idstr]["views"] = UserViewQuestion.objects.filter(
                question_id=question_id
            ).count()

            options = {}
            for opt in option_ids:
                question = Question.objects.get(id=question_id)
                opt_index = question.order.index(opt.id)  # Use opt.id
                if opt_index in options:
                    options[opt_index] += 1
                else:
                    options[opt_index] = 1

            questions[q_idstr]["options"] = options

            if text:
                questions[q_idstr]["ans"].append(text)  # Append answer
        return Response({"report": report}, status=status.HTTP_200_OK)
