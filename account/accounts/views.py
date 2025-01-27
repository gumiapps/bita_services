from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    PasswordResetSerializer,
    SetNewPasswordSerializer,
    PasswordChangeSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .permissions import IsOwnerOrAdmin
from .models import User
from django.shortcuts import render

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ["retrieve", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        return super().get_permissions()


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password reset link sent."}, status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user)
        return Response(
            {"detail": "Password has been reset."}, status=status.HTTP_200_OK
        )


class PasswordChangeView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user)
        update_session_auth_hash(request, user)  # Keep the user logged in
        return Response(
            {"detail": "Password has been changed."}, status=status.HTTP_200_OK
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


def api_documentation(request):
    return render(request, "index.html")
