from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Profile
from rest_framework.validators import UniqueValidator

class PasswordConfirmationMixin:
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Password fields did not match.'})

        return data

class SignUpSerializer(
    PasswordConfirmationMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'password2',
            'email',
            'phone_number',
        )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class LoginSerializer(serializers.Serializer):  
    '''  
    This serializer will handle user login  
    '''  
    
    identifier = serializers.CharField()  # This will accept either an email, username, or phone number  
    password = serializers.CharField(write_only=True)  

    def validate(self, attrs):  
        identifier = attrs.get('identifier')  
        password = attrs.get('password') 
        print(identifier) 
        


        user = None  

       
        if "@" in identifier:  
            
            user = User.objects.get(email=identifier)  
        else:  
            try:  
             
                user = User.objects.get(username=identifier) 
                
                
            except User.DoesNotExist:  
                try:  
                 
                    user = User.objects.get(phone_number=identifier)  
                except User.DoesNotExist:  
                    user = None  

      
        if user is None or not user.check_password(password):  
            raise serializers.ValidationError("Invalid credentials. Please try again.")  

        attrs['user'] = user    
        return attrs  

    class Meta:  
        fields = ["identifier", "password"]     


class UserProfileSerializer(serializers.ModelSerializer):
    '''
    this serializer will handle user profile
    '''
    
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'profile_picture']
        extra_kwargs = {
            'user': {'read_only': True},
        }
    

class ChangePasswordSerializer(
    PasswordConfirmationMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = User
        fields = (
            'old_password',
            'password',
            'password2',
        )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )
    old_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'old_password': 'Old password is incorrect.'})

        return value

    def validate(self, data):
        data = super().validate(data)
        print(type(data))

        if data['old_password'] == data['password']:
            raise serializers.ValidationError({'password': 'Password should not be the same with old password.'})

        return data

    def create(self, validated_data):
        print(type(validated_data))
        print(validated_data)
        user = self.context['request'].user
        user.set_password(validated_data['password'])
        user.save()

        return user        