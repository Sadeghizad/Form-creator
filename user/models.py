from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import re
from django.core.exceptions import ValidationError
def validate_phone_number(value):
    reg = re.compile(r'^(09\d{9}|\+989\d{9}|00989\d{9})$')
    if not reg.match(value) :
        raise ValidationError('Your Phone Number is incorrect')

class User(AbstractUser):
    role = models.CharField(
        max_length=20, choices=[("admin", "Admin"), ("user", "User")]
    )
    updated_at = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=13, validators=[validate_phone_number], unique=True, null=True, blank=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

