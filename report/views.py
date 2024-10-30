from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from report.tasks import generate_admin_report
from .models import Report,UserViewQuestion,UserViewForm,AdminReport
from form.models import Answer,Question
from rest_framework.permissions import IsAdmin
class AdminReportView(APIView):
    permission_classes =IsAdmin
    def post(self, request):
        # Trigger the Celery task to update the form stats
        generate_admin_report.delay()

        return Response(
            {"message": "admin report update initiated. Check logs for progress."},
            status=status.HTTP_200_OK
        )
    def get(self,request):
        return Response(AdminReport.objects.latest().report_data,status=status.HTTP_200_OK)
class UserReport(APIView):
    def post(self,request):
        formid=request.data.get("form_id")
        try:
            last_report=Report.objects.get(form_id=formid)
        except:
            last_report=None
        report={}
        if last_report:
            answers = Answer.objects.filter(form_id=formid,created_at__gte=last_report.timestamp)
            report = last_report.report
        else:
            answers = Answer.objects.filter(form_id=formid)
            report["form_id"]=formid
            report["views"]=UserViewForm.objects.filter(form_id=formid).count()
            report['questions']={}
            questions={}
        for answer in answers:
            question_id = answer.question
            option_ids = None
            text=answer.text
            if answer.option:
                option_ids = list(answer.option.id)
            if answer.select:
                option_ids = list(answer.select)
            if not answer.text:
                answer.text = None
            questions[question_id]['views']=UserViewQuestion.objects.filter(form_id=formid).count()
            options={}
            for opt in option_ids:
                opt=Question.objects.get(id=question_id).order.index(opt)
                if options[opt]:
                    options[opt] += 1
                options[opt]=1
            questions[question_id]=options
            if text:
                if not questions[question_id]['ans']:
                    questions[question_id]['ans']=[]
                questions[question_id]['ans'].append(text)
        return Response(
            {"report": report},
            status=status.HTTP_200_OK
        )