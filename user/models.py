from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
import re
from django.dispatch import receiver
from django.db.models.signals import post_save

def validate_phone_number(value):
    reg = re.compile(r'^(09\d{9}|\+989\d{9}|00989\d{9})$')
    if not reg.match(value) :
        raise ValidationError('Your Phone Number is incorrect')

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('User', 'User')], default='User')
    updated_at = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=13, validators=[validate_phone_number], unique=True, null=True, blank=True)
    
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Custom related name to avoid clash
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # Custom related name to avoid clash
        blank=True
    )
    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        profile.save()      