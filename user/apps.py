from django.apps import AppConfig

from django.core.mail import send_mail
from django.conf import settings

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

from django.core.mail import send_mail
from django.conf import settings

def send_custom_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )