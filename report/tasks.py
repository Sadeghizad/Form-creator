from celery import shared_task
from services.neo4j_service import neo4j_service
from form.models import User, Form, Process, Question, Answer
from django.utils import timezone
from datetime import timedelta
import json

@shared_task
def update_form_stats():
    # Fetch new answers
    new_answers = Answer.objects.filter(created_at__gte=last_run_timestamp)

    # Aggregate and update stats in Neo4j
    for answer in new_answers:
        form_id = answer.question.form.id
        question_id = answer.question.id
        if answer.option:
            option_id = answer.option.id
        else:
            option_id = None
        
        # Build the data structure similar to what you described
        data = {
            "question": question_id,
            "option": option_id,
            "answer_text": answer.text,
        }
        
        # Update the Neo4j database
        query = """
        MERGE (f:Form {id: $form_id})
        MERGE (q:Question {id: $question_id})
        MERGE (f)-[:HAS_QUESTION]->(q)
        MERGE (o:Option {id: $option_id})
        MERGE (q)-[:HAS_OPTION]->(o)
        SET o.count = coalesce(o.count, 0) + 1
        """
        parameters = {
            "form_id": form_id,
            "question_id": question_id,
            "option_id": option_id
        }
        neo4j_service.execute_query(query, parameters)

    print("Form stats updated.")

@shared_task
def generate_admin_report():
    now = timezone.now()
    # Time ranges
    last_24_hours = now - timedelta(days=1)
    last_week = now - timedelta(weeks=1)
    last_month = now - timedelta(weeks=4)

    # Total counts
    total_users = User.objects.count()
    total_forms = Form.objects.count()
    total_processes = Process.objects.count()
    total_questions = Question.objects.count()
    total_answers = Answer.objects.count()

    # Changes in the last 24 hours
    users_24h = User.objects.filter(created_at__gte=last_24_hours).count()
    forms_24h = Form.objects.filter(created_at__gte=last_24_hours).count()
    processes_24h = Process.objects.filter(created_at__gte=last_24_hours).count()
    questions_24h = Question.objects.filter(created_at__gte=last_24_hours).count()
    answers_24h = Answer.objects.filter(created_at__gte=last_24_hours).count()

    # Changes in the last week
    users_week = User.objects.filter(created_at__gte=last_week).count()
    forms_week = Form.objects.filter(created_at__gte=last_week).count()
    processes_week = Process.objects.filter(created_at__gte=last_week).count()
    questions_week = Question.objects.filter(created_at__gte=last_week).count()
    answers_week = Answer.objects.filter(created_at__gte=last_week).count()

    # Changes in the last month
    users_month = User.objects.filter(created_at__gte=last_month).count()
    forms_month = Form.objects.filter(created_at__gte=last_month).count()
    processes_month = Process.objects.filter(created_at__gte=last_month).count()
    questions_month = Question.objects.filter(created_at__gte=last_month).count()
    answers_month = Answer.objects.filter(created_at__gte=last_month).count()

    report_data = {
        "timestamp": now.isoformat(),
        "users": total_users,
        "forms": total_forms,
        "processes": total_processes,
        "questions": total_questions,
        "answers": total_answers,
        "last24hourchanges": {
            "users": users_24h,
            "forms": forms_24h,
            "processes": processes_24h,
            "questions": questions_24h,
            "answers": answers_24h,
        },
        "lastweekhourchanges": {
            "users": users_week,
            "forms": forms_week,
            "processes": processes_week,
            "questions": questions_week,
            "answers": answers_week,
        },
        "lastmonthhourchanges": {
            "users": users_month,
            "forms": forms_month,
            "processes": processes_month,
            "questions": questions_month,
            "answers": answers_month,
        },
    }
    AdminReport.objects.create(timestamp=now, report_data=report_data)
    # Save the report to a database model or cache (optional)
    # You can also log it or save it as a JSON file
    return json.dumps(report_data)
