from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserCRUDAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            phone="912345678",
            password="adminpass123",
        )
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regularuser@example.com",
            phone="912345679",
            password="userpass123",
        )
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "phone": "912345432",
            "password": "testpass123",
        }

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_user(self):
        """Test creating a new user."""
        url = reverse("user-list")
        response = self.client.post(url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(
            User.objects.get(username="testuser").email, "testuser@example.com"
        )

    def test_admin_can_list_users(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_list_users(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_own_user(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-detail", args=[self.regular_user.id])
        response = self.client.patch(url, {"email": "newemail@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, "newemail@example.com")

    def test_admin_can_update_any_user(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-detail", args=[self.regular_user.id])
        response = self.client.patch(url, {"email": "adminupdated@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, "adminupdated@example.com")

    def test_non_owner_cannot_update_user(self):
        another_user = User.objects.create_user(
            username="anotheruser",
            email="anotheruser@example.com",
            phone="912345680",
            password="anotherpass123",
        )
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-detail", args=[another_user.id])
        response = self.client.patch(url, {"email": "unauthorized@example.com"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_own_user(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-detail", args=[self.regular_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.regular_user.id).exists())

    def test_admin_can_delete_any_user(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-detail", args=[self.regular_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.regular_user.id).exists())

    def test_non_owner_cannot_delete_user(self):
        another_user = User.objects.create_user(
            username="anotheruser",
            email="anotheruser@example.com",
            phone="912345680",
            password="anotherpass123",
        )
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("user-detail", args=[another_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_list_users(self):
        self.client.credentials()  # Remove any credentials
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_retrieve_user(self):
        self.client.credentials()  # Remove any credentials
        user = User.objects.get(username="admin")
        url = reverse("user-detail", args=[user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_update_user(self):
        self.client.credentials()  # Remove any credentials
        user = User.objects.get(username="admin")
        url = reverse("user-detail", args=[user.id])
        data = {
            "username": "admin_updated",
            "email": "admin_updated@example.com",
            "phone": "987654321",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_delete_user(self):
        self.client.credentials()  # Remove any credentials
        user = User.objects.get(username="admin")
        url = reverse("user-detail", args=[user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("password-change")
        data = {
            "old_password": "userpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password("newpass123"))

    def test_password_reset(self):
        url = reverse("password-reset")
        data = {
            "email": self.regular_user.email,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm(self):
        url = reverse("password-reset")
        data = {
            "email": self.regular_user.email,
        }
        self.client.post(url, data, format="json")

        # Simulate the token and uid generation
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator

        uid = urlsafe_base64_encode(force_bytes(self.regular_user.pk))
        token = default_token_generator.make_token(self.regular_user)

        url = reverse("password-reset-confirm", args=[uid, token])
        data = {
            "password": "newpass123",
            "password_confirm": "newpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password("newpass123"))

    def test_authentication(self):
        url = reverse("token_obtain_pair")
        data = {
            "phone": self.regular_user.phone,
            "password": "userpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
