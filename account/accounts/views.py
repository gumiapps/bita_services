import json
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from .serializers import (
    PasswordResetSerializer,
    SetNewPasswordSerializer,
    PasswordChangeSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    SupplierSerializer,
    CustomerSerializer,
    BusinessSerializer,
    EmployeeSerializer,
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .permissions import (
    IsOwnerOrAdmin,
    IsBusinessOwnerOrAdmin,
    EmployeeCreatePermission,
    EmployeeUpdatePermission,
    EmployeeDeletePermission,
    EmployeeRetrievePermission,
    IsNonEmployeeUser,
)
from .models import User, Supplier, Customer, Business, Employee
from django.shortcuts import render
from rest_framework_simplejwt.tokens import AccessToken
import requests
from django.conf import settings
from .models import EmployeeInvitation
from .serializers import (
    EmployeeInvitationSerializer,
)  # create one for invitation if needed

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

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH")


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == "create":
            self.permission_classes = [IsAuthenticated, IsNonEmployeeUser]
        else:
            self.permission_classes = [IsAuthenticated, IsBusinessOwnerOrAdmin]
        return super().get_permissions()


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def create(self, request, *args, **kwargs):
        return Response(
            {
                "detail": "Direct employee creation is forbidden. Use the invitation endpoint."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            self.permission_classes = [
                IsAuthenticated,
                IsOwnerOrAdmin,
                EmployeeUpdatePermission,
            ]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, EmployeeDeletePermission]
        elif self.action == "retrieve":
            self.permission_classes = [IsAuthenticated, EmployeeRetrievePermission]
        else:
            self.permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        return super().get_permissions()


class JWTTokenVerifyView(TokenVerifyView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            # Validate the token using the parent serializer
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"detail": "Token is invalid or expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Decode token and fetch user data
        token = request.data.get("token")
        access_token = AccessToken(token)
        user_id = access_token.get("user_id")
        user = User.objects.get(id=user_id)
        user_data = UserSerializer(user).data
        user_data.update({"id": user_id})

        return Response(
            {"detail": "Token is valid", "user": user_data},
            status=status.HTTP_200_OK,
        )


class EmployeeInvitationCreateView(generics.CreateAPIView):
    """
    Creates an invitation for an employee and sends an invitation email.
    """

    serializer_class = EmployeeInvitationSerializer
    permission_classes = [IsAuthenticated, EmployeeCreatePermission]

    def perform_create(self, serializer):
        invitation = serializer.save(created_by=self.request.user)
        # Construct the acceptance URL. Adjust BASE_URL as appropriate.
        request = self.request
        acceptance_link = f"{request.scheme}://{request.get_host()}/employee/invite/accept/{invitation.token}/"
        # Send invitation email via NOTIFICATION_API.
        email_url = settings.EMAIL_URL
        notification_api_key = settings.NOTIFICATION_API_KEY
        payload = json.dumps(
            {
                "subject": "You're Invited to Join as an Employee",
                "message": f"Please click the following link to accept your invitation: {acceptance_link}",
                "recipients": invitation.email,
            }
        )
        headers = {
            "Authorization": f"Api-Key {notification_api_key}",
            "Content-Type": "application/json",
        }
        response = requests.request("POST", email_url, headers=headers, data=payload)


class EmployeeInvitationAcceptView(generics.GenericAPIView):
    """
    Accepts an invitation to become an employee immediately when the invitation link is clicked.
    Processes the invitation via a GET request and returns a JSON response.
    """

    permission_classes = [AllowAny]

    def post(self, request, token):
        try:
            invitation = EmployeeInvitation.objects.get(token=token, accepted=False)
        except EmployeeInvitation.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired invitation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create the employee using invitation data with a temporary password.
        employee = Employee.objects.create_user(
            email=invitation.email,
            phone=invitation.phone,
            password="password",  # Temporary password
            business=invitation.business,
        )
        employee.first_name = invitation.first_name
        employee.last_name = invitation.last_name
        employee.role = invitation.role
        employee.created_by = invitation.created_by
        employee.save()

        # Mark invitation as accepted.
        invitation.accepted = True
        invitation.save()

        # Send congratulatory email via NOTIFICATION_API.
        email_url = settings.EMAIL_URL
        notification_api_key = settings.NOTIFICATION_API_KEY
        payload = json.dumps(
            {
                "subject": "Welcome Aboard!",
                "message": (
                    "Congratulations on joining our team. Your default password is 'password'. "
                    "Please change it after logging in."
                ),
                "recipients": invitation.email,
            }
        )
        headers = {
            "Authorization": f"Api-Key {notification_api_key}",
            "Content-Type": "application/json",
        }
        requests.request("POST", email_url, headers=headers, data=payload)

        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def api_documentation(request):
    return render(request, "index.html")
