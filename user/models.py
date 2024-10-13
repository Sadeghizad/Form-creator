from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission



class User(AbstractUser):
    role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('user', 'User')])
    updated_at = models.DateTimeField(auto_now=True)
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
