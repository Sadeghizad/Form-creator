from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User  
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from .models import *

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number']



class CustomRegisterSerializer(RegisterSerializer):
    phone_number = serializers.CharField(required=True)
    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    def get_cleaned_data(self):
        data = super().get_cleaned_data()  
        data['phone_number'] = self.validated_data.get('phone_number', '')
        return data

    def save(self, request):
        user = super().save(request)  
        self.cleaned_data = self.get_cleaned_data()

        
        user.phone_number = self.cleaned_data.get('phone_number')
        user.save()  

        return user



class CustomLoginSerializer(LoginSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    totp_code = serializers.CharField(required=False, allow_blank=True)
    email_pin = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        
        username = data.get('username')
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not username and not email and not phone_number:
            raise serializers.ValidationError("One of username, email, or phone number must be provided.")

        user = None
        if username:
            user = authenticate(username=username, password=password)
        elif email:
            user = authenticate(email=email, password=password)
        elif phone_number:
            try:
                user_obj = User.objects.get(phone_number=phone_number)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid phone number.")
        
        if not user:
            raise serializers.ValidationError("Invalid credentials or account is not active.")

        if user and user.enable_2fa:
            if user.use_email_for_2fa:
                email_pin = data.get("email_pin")
                if not email_pin:
                    user.generate_email_pin()
                    raise serializers.ValidationError("Enter the PIN sent to your email.")
                elif email_pin != user.email_pin:
                    raise serializers.ValidationError("Invalid email PIN.")
                user.email_pin = None
                user.save()
            else:
                totp_code = data.get("totp_code")
                if not totp_code:
                    raise serializers.ValidationError("Enter the TOTP code from Google Authenticator.")
                if not user.verify_totp(totp_code):
                    raise serializers.ValidationError("Invalid TOTP code.")
                
        if user and not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        
        # if email and not user.emailaddress_set.filter(verified=True).exists():
        #     raise serializers.ValidationError("E-mail is not verified.")

        if user and not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        
        return {'user': user}