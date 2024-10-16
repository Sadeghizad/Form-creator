from dj_rest_auth.views import PasswordResetConfirmView
from .serializers import CustomLoginSerializer
from dj_rest_auth.views import LoginView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
class CustomLoginView(LoginView):
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer
    def post(self, request, *args, **kwargs):
        
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        
        return Response({
            'refresh': str(refresh),
            'access': access_token,
        })
    


def password_reset_confirm_view(request, *args, **kwargs):
    return PasswordResetConfirmView.as_view()(request, *args, **kwargs)