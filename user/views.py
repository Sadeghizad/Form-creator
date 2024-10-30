from rest_framework import viewsets
from rest_framework import status
from dj_rest_auth.views import PasswordResetConfirmView
from .serializers import CustomLoginSerializer, CustomRegisterSerializer
from dj_rest_auth.views import LoginView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

import qrcode
from io import BytesIO
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import HttpResponse


class CustomLoginView(LoginView):
    permission_classes = [AllowAny]
    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response(
            {
                "refresh": str(refresh),
                "access": access_token,
            }
        )


def password_reset_confirm_view(request, *args, **kwargs):
    return PasswordResetConfirmView.as_view()(request, *args, **kwargs)


class CustomRegisterViewSet(viewsets.ViewSet):
    """
    A viewset for registering a new user with an additional phone number field.
    """

    permission_classes = [AllowAny]
    serializer_class = CustomRegisterSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save(request)
            return Response(
                {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "phone_number": user.phone_number,
                    }
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateQRView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        user.generate_totp_secret()
        uri = user.get_totp_uri()

        qr = qrcode.make(uri)
        stream = BytesIO()
        qr.save(stream, "PNG")
        return HttpResponse(stream.getvalue(), content_type="image/png")


class Update2FASettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        enable_2fa = request.data.get("enable_2fa")
        use_email_for_2fa = request.data.get("use_email_for_2fa")

        user.enable_2fa = enable_2fa
        user.use_email_for_2fa = use_email_for_2fa

        if enable_2fa and not use_email_for_2fa:
            user.generate_totp_secret()

        user.save()
        return Response({"message": "2FA settings updated successfully."})
