from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Supplier, Customer

User = get_user_model()


class UserCRUDAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            phone="912345678",
            password="adminpass123",
        )
        self.regular_user = User.objects.create_user(
            email="regularuser@example.com",
            phone="912345679",
            password="userpass123",
        )
        self.user_data = {
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
        user = User.objects.get(email="admin@example.com")
        url = reverse("user-detail", args=[user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_update_user(self):
        self.client.credentials()  # Remove any credentials
        user = User.objects.get(email="admin@example.com")
        url = reverse("user-detail", args=[user.id])
        data = {
            "email": "admin_updated@example.com",
            "phone": "987654321",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_delete_user(self):
        self.client.credentials()  # Remove any credentials
        user = User.objects.get(email="admin@example.com")
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

    def test_password_reset_confirm(self):
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

    def test_authentication_via_phone(self):
        url = reverse("token_obtain_pair")
        data = {
            "identifier": self.regular_user.phone,
            "password": "userpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_authentication_via_email(self):
        url = reverse("token_obtain_pair")
        data = {
            "identifier": self.regular_user.email,
            "password": "userpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class SupplierCRUDAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            phone="912345678",
            password="adminpass123",
        )
        self.supplier_data = {
            "name": "Supplier 1",
            "phone": "912345678",
            "email": "supplier1@example.com",
            "address": "Supplier 1 address",
        }

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_supplier(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("supplier-list")
        response = self.client.post(url, self.supplier_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 1)

    def test_admin_can_list_suppliers(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("supplier-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_retrieve_supplier(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_supplier(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        data = {
            "name": "Supplier 2",
            "phone": "912345679",
            "email": "supplier2@example.com",
            "address": "Supplier 2 address",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        supplier.refresh_from_db()
        self.assertEqual(supplier.name, "Supplier 2")

    def test_admin_can_delete_supplier(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Supplier.objects.filter(id=supplier.id).exists())

    def test_unauthorized_user_cannot_list_suppliers(self):
        self.client.credentials()
        url = reverse("supplier-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_retrieve_supplier(self):
        self.client.credentials()
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_update_supplier(self):
        self.client.credentials()
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        data = {
            "name": "Unauthorized Supplier",
            "phone": "912345679",
            "email": "unauth@example.com",
            "address": "Unauthorized Supplier address",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_delete_supplier(self):
        self.client.credentials()
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerCRUDAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            phone="912345678",
            password="adminpass123",
        )
        self.customer_data = {
            "first_name": "Customer",
            "last_name": "1",
            "phone": "912345678",
            "email": "customer1@example.com",
            "address": "Customer 1 address",
        }

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_create_customer(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("customer-list")
        response = self.client.post(url, self.customer_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)

    def test_admin_can_list_customers(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("customer-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_retrieve_customer(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_customer(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        data = {
            "first_name": "Customer",
            "last_name": "2",
            "phone": "912345679",
            "email": "customer2@example.com",
            "address": "Customer 2 address",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        self.assertEqual(customer.last_name, "2")

    def test_admin_can_delete_customer(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Customer.objects.filter(id=customer.id).exists())

    def test_unauthorized_user_cannot_list_customers(self):
        self.client.credentials()
        url = reverse("customer-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_retrieve_customer(self):
        self.client.credentials()
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_update_customer(self):
        self.client.credentials()
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        data = {
            "first_name": "Unauthorized Customer",
            "last_name": "1",
            "phone": "912345679",
            "email": "unauth@example.com",
            "address": "Unauthorized Customer address",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_cannot_delete_customer(self):
        self.client.credentials()
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerSupplierPermissionTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            phone="912345678",
            password="adminpass123",
        )
        self.regular_user = User.objects.create_user(
            email="regular@example.com",
            phone="912345679",
            password="userpass123",
        )
        # Sample data for customer and supplier
        self.customer_data = {
            "first_name": "Customer",
            "last_name": "Test",
            "phone": "912345678",
            "email": "customer@example.com",
            "address": "Customer Address",
        }
        self.supplier_data = {
            "name": "Supplier Test",
            "phone": "912345678",
            "email": "supplier@example.com",
            "address": "Supplier Address",
        }

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    # --- Customer endpoint tests ---

    def test_owner_can_update_own_customer(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        # Create customer with created_by set to the regular user
        customer = Customer.objects.create(
            created_by=self.regular_user, **self.customer_data
        )
        url = reverse("customer-detail", args=[customer.id])
        data = {
            "first_name": "Updated",
            "last_name": customer.last_name,
            "phone": customer.phone,
            "email": customer.email,
            "address": customer.address,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        self.assertEqual(customer.first_name, "Updated")

    def test_non_owner_cannot_update_customer(self):
        # Create a customer with created_by as a different user
        owner = User.objects.create_user(
            email="owner@example.com",
            phone="912345100",
            password="ownerpass123",
        )
        customer = Customer.objects.create(created_by=owner, **self.customer_data)
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("customer-detail", args=[customer.id])
        data = {"first_name": "Hacked"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_customer(self):
        customer = Customer.objects.create(
            created_by=self.regular_user, **self.customer_data
        )
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("customer-detail", args=[customer.id])
        data = {"first_name": "AdminUpdated"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Supplier endpoint tests ---

    def test_owner_can_update_own_supplier(self):
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        supplier = Supplier.objects.create(
            created_by=self.regular_user, **self.supplier_data
        )
        url = reverse("supplier-detail", args=[supplier.id])
        data = {
            "name": "Updated Supplier",
            "phone": supplier.phone,
            "email": supplier.email,
            "address": supplier.address,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        supplier.refresh_from_db()
        self.assertEqual(supplier.name, "Updated Supplier")

    def test_non_owner_cannot_update_supplier(self):
        owner = User.objects.create_user(
            email="owner2@example.com",
            phone="912345222",
            password="ownerpass222",
        )
        supplier = Supplier.objects.create(created_by=owner, **self.supplier_data)
        token = self.get_jwt_token(self.regular_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("supplier-detail", args=[supplier.id])
        data = {"name": "Hacked Supplier"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_supplier(self):
        supplier = Supplier.objects.create(
            created_by=self.regular_user, **self.supplier_data
        )
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("supplier-detail", args=[supplier.id])
        data = {"name": "Admin Updated Supplier"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JWTTokenVerifyTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            phone="912345678",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_valid_token_verification(self):
        token = self.get_jwt_token(self.user)
        url = reverse("token_verify")
        response = self.client.post(url, {"token": token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_invalid_token_verification(self):
        url = reverse("token_verify")
        response = self.client.post(url, {"token": "invalidtoken"}, format="json")
        # Expecting a 401 Unauthorized for an invalid token
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
