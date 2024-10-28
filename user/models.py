from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import re
from django.core.exceptions import ValidationError

import pyotp
import random
from django.core.mail import send_mail

from user.apps import send_custom_email

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

    enable_2fa = models.BooleanField(default=False)
    use_email_for_2fa = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=16, blank=True, null=True)
    email_pin = models.CharField(max_length=6, blank=True, null=True)

    def generate_totp_secret(self):
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()  
            self.save()
        return self.totp_secret

    def get_totp_uri(self):
        return f"otpauth://totp/Form-Creator:{self.username}?secret={self.totp_secret}&issuer=form-creator"

    def verify_totp(self, token):
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token)

    def generate_email_pin(self):
        pin = f"{random.randint(100000, 999999)}"
        self.email_pin = pin
        self.save()

        send_custom_email(
            subject="Your 2FA PIN Code",
            message=f"Your 2FA PIN code is {pin}",
            recipient_list=[self.email],
        )
        return pin
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)