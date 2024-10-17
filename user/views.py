from django.shortcuts import render
from .serializers import SignUpSerializer
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken  
from rest_framework.response import Response  
from rest_framework.permissions import AllowAny   
from .serializers import LoginSerializer, UserProfileSerializer, ChangePasswordSerializer
from .models import User, Profile
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
import requests  
from django.views import View  
from django.http import JsonResponse  
from rest_framework.views import APIView  
from requests.exceptions import RequestException

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (
        AllowAny,
    )
    serializer_class = SignUpSerializer

class LoginView(generics.GenericAPIView):  
    """  
    View for user login, allowing authentication via email, username, or phone number.  
    """  
    serializer_class = LoginSerializer  
    permission_classes = [AllowAny]   

    def post(self, request, *args, **kwargs):  
        serializer = self.get_serializer(data=request.data)  
        serializer.is_valid(raise_exception=True)  
        
         
        user = serializer.validated_data['user']  

          
        token = self.get_token_for_user(user)   

          
        return Response({  
            "message": "Login successful",  
             "token": token,    
            "user": {  
                "id": user.id,  
                "username": user.username,  
                "email": user.email,  
                 
            }  
        }, status=status.HTTP_200_OK) 

    def get_token_for_user(self, user):  
        refresh = RefreshToken.for_user(user)  
        return {  
            'refresh': str(refresh),  
            'access': str(refresh.access_token),  
        }  

class UpdateProfileViewSet(viewsets.ModelViewSet):  
    permission_classes = [IsAuthenticated]  
    serializer_class = UserProfileSerializer  

    def retrieve(self, request, pk=None):  
     
        try:  
            subscription = Subscription.objects.get(pk=pk, user=request.user, is_active=True)  
        except Subscription.DoesNotExist:  
            return Response({"error": "Subscription not found or you do not have permission to view it."},   
                            status=status.HTTP_404_NOT_FOUND)  

        days_left = (subscription.end_date - datetime.now().date()).days  

        
        subscription_data = SubscriptionSerializer(subscription).data  
        subscription_data['days_left'] = days_left  

        return Response(subscription_data, status=status.HTTP_200_OK)    

    def create(self, request, *args, **kwargs):  
        return Response({'detail': 'Profile creation is not allowed.'}, status=status.HTTP_403_FORBIDDEN)  

    def destroy(self, request, *args, **kwargs):  
        return Response({'detail': 'Profile deletion is not allowed.'}, status=status.HTTP_403_FORBIDDEN)  

    def update(self, request, *args, **kwargs):  
        partial = kwargs.pop('partial', False)   
        instance = self.get_object()  
        serializer = self.get_serializer(instance, data=request.data, partial=partial)  
        serializer.is_valid(raise_exception=True)  
        self.perform_update(serializer)  

        return Response(serializer.data) 

class ChangePasswordView(generics.GenericAPIView):
    """
    Returns a list of all **active** accounts in the system.

    For more details on how accounts are activated please [see here][ref].

    [ref]: http://example.com/activating-accounts
    """
    permission_classes = (
        IsAuthenticated,
    )
    serializer_class = ChangePasswordSerializer
    
    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({'success': True})        
