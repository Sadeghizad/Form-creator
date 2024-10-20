from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from report.tasks import update_form_stats

class UpdateFormStatsView(APIView):
    def post(self, request):
        # Trigger the Celery task to update the form stats
        update_form_stats.delay()

        return Response(
            {"message": "Form stats update initiated. Check logs for progress."},
            status=status.HTTP_200_OK
        )
