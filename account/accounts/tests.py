from environs import Env
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Supplier, Customer, Business, Employee

env = Env()
env.read_env()

User = get_user_model()


class BaseAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        # Set the API key header for all client requests.
        self.client.defaults["HTTP_X_API_KEY"] = env.str("TEST_API_KEY")

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def get_api_key(self):
        return {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}


class UserCRUDAPITestCase(BaseAPITestCase):
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

    def test_create_user(self):
        """Test creating a new user."""
        url = reverse("user-list")
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.post(url, self.user_data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_admin_can_list_users(self):
        token = self.get_jwt_token(self.admin_user)
        url = reverse("user-list")
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_list_users(self):
        token = self.get_jwt_token(self.regular_user)
        url = reverse("user-list")
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        headers.update(self.get_api_key())
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_own_user(self):
        token = self.get_jwt_token(self.regular_user)
        url = reverse("user-detail", args=[self.regular_user.id])
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}
        headers.update(self.get_api_key())
        response = self.client.patch(url, {"email": "newemail@example.com"}, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, "newemail@example.com")

    def test_admin_can_update_any_user(self):
        token = self.get_jwt_token(self.admin_user)
        url = reverse("user-detail", args=[self.regular_user.id])
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.patch(
            url, {"email": "adminupdated@example.com"}, **headers
        )
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
        url = reverse("user-detail", args=[another_user.id])
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
        }
        response = self.client.patch(
            url, {"email": "unauthorized@example.com"}, **headers
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_own_user(self):
        token = self.get_jwt_token(self.regular_user)
        url = reverse("user-detail", args=[self.regular_user.id])
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.regular_user.id).exists())

    def test_admin_can_delete_any_user(self):
        token = self.get_jwt_token(self.admin_user)
        url = reverse("user-detail", args=[self.regular_user.id])
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.regular_user.id).exists())

    def test_non_owner_cannot_delete_user(self):
        another_user = User.objects.create_user(
            email="anotheruser@example.com",
            phone="912345680",
            password="anotherpass123",
        )
        token = self.get_jwt_token(self.regular_user)
        url = reverse("user-detail", args=[another_user.id])
        headers = {
            "Authorization": f"Bearer {token}",
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_list_users(self):
        url = reverse("user-list")
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_retrieve_user(self):
        user = User.objects.get(email="admin@example.com")
        url = reverse("user-detail", args=[user.id])
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_update_user(self):
        user = User.objects.get(email="admin@example.com")
        url = reverse("user-detail", args=[user.id])
        data = {
            "email": "admin_updated@example.com",
            "phone": "987654321",
        }
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.put(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_delete_user(self):
        user = User.objects.get(email="admin@example.com")
        url = reverse("user-detail", args=[user.id])
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_password_change(self):
        token = self.get_jwt_token(self.regular_user)
        url = reverse("password-change")
        data = {
            "old_password": "userpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.put(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password("newpass123"))

    def test_password_reset_confirm(self):
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
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password("newpass123"))

    def test_authentication_via_phone(self):
        url = reverse("token_obtain_pair")
        data = {
            "identifier": self.regular_user.phone,
            "password": "userpass123",
        }
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_authentication_via_email(self):
        url = reverse("token_obtain_pair")
        data = {
            "identifier": self.regular_user.email,
            "password": "userpass123",
        }
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class SupplierCRUDAPITestCase(BaseAPITestCase):
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

    def test_create_supplier(self):
        token = self.get_jwt_token(self.admin_user)
        url = reverse("supplier-list")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
        }
        response = self.client.post(url, self.supplier_data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 1)

    def test_admin_can_list_suppliers(self):
        token = self.get_jwt_token(self.admin_user)
        url = reverse("supplier-list")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_retrieve_supplier(self):
        token = self.get_jwt_token(self.admin_user)
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_supplier(self):
        token = self.get_jwt_token(self.admin_user)
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        data = {
            "name": "Supplier 2",
            "phone": "912345679",
            "email": "supplier2@example.com",
            "address": "Supplier 2 address",
        }
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.put(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        supplier.refresh_from_db()
        self.assertEqual(supplier.name, "Supplier 2")

    def test_admin_can_delete_supplier(self):
        token = self.get_jwt_token(self.admin_user)
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Supplier.objects.filter(id=supplier.id).exists())

    def test_unauthorized_user_cannot_list_suppliers(self):
        url = reverse("supplier-list")
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_retrieve_supplier(self):
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_update_supplier(self):
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        data = {
            "name": "Unauthorized Supplier",
            "phone": "912345679",
            "email": "unauth@example.com",
            "address": "Unauthorized Supplier address",
        }
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.put(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_delete_supplier(self):
        supplier = Supplier.objects.create(**self.supplier_data)
        url = reverse("supplier-detail", args=[supplier.id])
        headers = {"HTTP_X_API_KEY": env.str("TEST_API_KEY")}
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CustomerCRUDAPITestCase(BaseAPITestCase):
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

    def test_create_customer(self):
        token = self.get_jwt_token(self.admin_user)
        url = reverse("customer-list")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
        }
        response = self.client.post(url, self.customer_data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)

    def test_admin_can_list_customers(self):
        token = self.get_jwt_token(self.admin_user)
        url = reverse("customer-list")
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_retrieve_customer(self):
        token = self.get_jwt_token(self.admin_user)
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
        }
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_customer(self):
        token = self.get_jwt_token(self.admin_user)
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        data = {
            "first_name": "Customer",
            "last_name": "2",
            "phone": "912345679",
            "email": "customer2@example.com",
            "address": "Customer 2 address",
        }
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
        }
        response = self.client.put(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        self.assertEqual(customer.last_name, "2")

    def test_admin_can_delete_customer(self):
        token = self.get_jwt_token(self.admin_user)
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
        }
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Customer.objects.filter(id=customer.id).exists())

    def test_unauthorized_user_cannot_list_customers(self):
        url = reverse("customer-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_retrieve_customer(self):
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_update_customer(self):
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_user_cannot_delete_customer(self):
        customer = Customer.objects.create(**self.customer_data)
        url = reverse("customer-detail", args=[customer.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CustomerSupplierPermissionTestCase(BaseAPITestCase):
    def setUp(self):
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

    # --- Customer endpoint tests ---

    def test_owner_can_update_own_customer(self):
        token = self.get_jwt_token(self.regular_user)
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
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.patch(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        customer.refresh_from_db()
        self.assertEqual(customer.first_name, "Updated")

    def test_non_owner_cannot_update_customer(self):
        owner = User.objects.create_user(
            email="owner@example.com",
            phone="912345100",
            password="ownerpass123",
        )
        customer = Customer.objects.create(created_by=owner, **self.customer_data)
        token = self.get_jwt_token(self.regular_user)
        url = reverse("customer-detail", args=[customer.id])
        data = {"first_name": "Hacked"}
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.patch(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_customer(self):
        customer = Customer.objects.create(
            created_by=self.regular_user, **self.customer_data
        )
        token = self.get_jwt_token(self.admin_user)
        url = reverse("customer-detail", args=[customer.id])
        data = {"first_name": "AdminUpdated"}
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.patch(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Supplier endpoint tests ---

    def test_owner_can_update_own_supplier(self):
        token = self.get_jwt_token(self.regular_user)
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
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.patch(url, data, format="json", **headers)
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
        url = reverse("supplier-detail", args=[supplier.id])
        data = {"name": "Hacked Supplier"}
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.patch(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_any_supplier(self):
        supplier = Supplier.objects.create(
            created_by=self.regular_user, **self.supplier_data
        )
        token = self.get_jwt_token(self.admin_user)
        url = reverse("supplier-detail", args=[supplier.id])
        data = {"name": "Admin Updated Supplier"}
        headers = {
            "HTTP_X_API_KEY": env.str("TEST_API_KEY"),
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        response = self.client.patch(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class JWTTokenVerifyTestCase(BaseAPITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            phone="912345678",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_valid_token_verification(self):
        token = self.get_jwt_token(self.user)
        url = reverse("token_verify")
        data = {"token": token}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_invalid_token_verification(self):
        url = reverse("token_verify")
        data = {"token": "invalidtoken"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BusinessCRUDAPITestCase(BaseAPITestCase):
    def setUp(self):
        # Create users for testing
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            phone="912345678",
            password="adminpass123",
        )
        self.owner_user = User.objects.create_user(
            email="owner@example.com",
            phone="912345679",
            password="ownerpass123",
        )
        self.regular_user = User.objects.create_user(
            email="regular@example.com",
            phone="912345680",
            password="userpass123",
        )
        # Create a business by owner_user
        self.business_data = {
            "name": "Test Business",
            "address": "123 Test Lane",
            "category": "Retail",
            "owner": self.owner_user,
        }
        self.business = Business.objects.create(**self.business_data)

    def get_auth_headers(self, user):
        token = self.get_jwt_token(user)
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        headers.update(self.get_api_key())
        return headers

    def test_admin_can_list_businesses(self):
        url = reverse("business-list")
        headers = self.get_auth_headers(self.admin_user)
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expect at least one business in the list
        self.assertGreaterEqual(len(response.data), 1)

    def test_non_admin_cannot_list_businesses(self):
        url = reverse("business-list")
        headers = self.get_auth_headers(self.regular_user)
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_retrieve_business(self):
        url = reverse("business-detail", args=[self.business.id])
        headers = self.get_auth_headers(self.owner_user)
        response = self.client.get(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("name"), self.business_data["name"])

    def test_non_owner_cannot_retrieve_business(self):
        url = reverse("business-detail", args=[self.business.id])
        headers = self.get_auth_headers(self.regular_user)
        response = self.client.get(url, **headers)
        # Non-owner, non-admin will be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_business(self):
        url = reverse("business-detail", args=[self.business.id])
        headers = self.get_auth_headers(self.owner_user)
        data = {"name": "Updated Business Name"}
        response = self.client.patch(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.business.refresh_from_db()
        self.assertEqual(self.business.name, data["name"])

    def test_non_owner_cannot_update_business(self):
        url = reverse("business-detail", args=[self.business.id])
        headers = self.get_auth_headers(self.regular_user)
        data = {"name": "Should Not Update"}
        response = self.client.patch(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_business(self):
        url = reverse("business-detail", args=[self.business.id])
        headers = self.get_auth_headers(self.admin_user)
        data = {"address": "456 Admin Ave"}
        response = self.client.patch(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.business.refresh_from_db()
        self.assertEqual(self.business.address, data["address"])

    def test_owner_can_delete_business(self):
        # Create a new business to test deletion
        business = Business.objects.create(
            name="Delete Test",
            address="Delete Address",
            category="Service",
            owner=self.owner_user,
        )
        url = reverse("business-detail", args=[business.id])
        headers = self.get_auth_headers(self.owner_user)
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Business.objects.filter(id=business.id).exists())

    def test_admin_can_delete_business(self):
        # Create a new business with owner_user as creator
        business = Business.objects.create(
            name="Admin Delete",
            address="Admin Delete Address",
            category="Tech",
            owner=self.owner_user,
        )
        url = reverse("business-detail", args=[business.id])
        headers = self.get_auth_headers(self.admin_user)
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Business.objects.filter(id=business.id).exists())

    def test_non_owner_cannot_delete_business(self):
        url = reverse("business-detail", args=[self.business.id])
        headers = self.get_auth_headers(self.regular_user)
        response = self.client.delete(url, **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Business should still exist
        self.assertTrue(Business.objects.filter(id=self.business.id).exists())


class EmployeeCRUDAPITestCase(BaseAPITestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_superuser(
            email="superadmin@example.com",
            phone="912345600",
            password="superadminpass",
        )
        self.owner_user = User.objects.create_user(
            email="owner@example.com",
            phone="912345601",
            password="ownerpass",
        )
        self.regular_user = User.objects.create_user(
            email="regular@example.com",
            phone="912345689",
            password="regularpass",
        )
        # Create a business owned by owner_user
        self.business = Business.objects.create(
            name="Employee Test Business",
            address="101 Business Ave",
            category="Services",
            owner=self.owner_user,
        )

        self.admin_employee_creator = Employee.objects.create_user(
            email="admindemo@example.com",
            phone="912345602",
            password="admindemopass",
            business=self.business,
        )
        self.admin_employee_creator.role = "Admin"
        self.admin_employee_creator.save(update_fields=["role"])

        self.manager_employee_creator = Employee.objects.create_user(
            email="managerdemo@example.com",
            phone="912345603",
            password="managerdemopass",
            business=self.business,
        )
        self.manager_employee_creator.role = "Manager"
        self.manager_employee_creator.save(update_fields=["role"])

        self.sales_user = Employee.objects.create_user(
            email="salesdemo@example.com",
            phone="912345604",
            password="salesdemopass",
            business=self.business,
        )
        self.sales_user.role = "Sales"
        self.sales_user.save(update_fields=["role"])

    def get_auth_headers(self, user):
        token = self.get_jwt_token(user)
        headers = {
            "HTTP_AUTHORIZATION": f"Bearer {token}",
        }
        headers.update(self.get_api_key())
        return headers

    # ----- Creation Tests -----
    def test_create_employee_by_business_owner(self):
        """
        Business owner can create any employee (including Admin).
        """
        url = reverse("employee-list")
        data = {
            "email": "newemployee@example.com",
            "first_name": "New",
            "last_name": "Employee",
            "phone": "912345605",
            "password": "newpass123",
            "role": "Admin",
            "created_by": self.owner_user.id,
            "business": self.business.id,
        }
        headers = self.get_auth_headers(self.owner_user)
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("role"), "Admin")

    def test_create_employee_by_admin_employee_allowed_roles(self):
        """
        An employee with Admin role can create Manager or Sales employees.
        """
        url = reverse("employee-list")
        # Allowed: creating a Manager employee
        data = {
            "email": "manager1@example.com",
            "first_name": "Manager",
            "last_name": "One",
            "phone": "912345606",
            "password": "managerpass1",
            "role": "Manager",
            "created_by": self.admin_employee_creator.id,
            "business": self.business.id,
        }
        headers = self.get_auth_headers(self.admin_employee_creator)
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Allowed: creating a Sales employee
        data["email"] = "sales1@example.com"
        data["role"] = "Sales"
        data["phone"] = "912345607"
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Not allowed: trying to create an Admin employee by non-owner creator
        data["email"] = "admin2@example.com"
        data["role"] = "Admin"
        data["phone"] = "912345608"
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_employee_by_manager_employee_allowed_roles(self):
        """
        A Manager employee can only create Sales employees.
        """
        url = reverse("employee-list")
        headers = self.get_auth_headers(self.manager_employee_creator)
        # Allowed: creating a Sales employee
        data = {
            "email": "sales2@example.com",
            "first_name": "Sales",
            "last_name": "Two",
            "phone": "912345609",
            "password": "salespass2",
            "role": "Sales",
            "created_by": self.manager_employee_creator.id,
            "business": self.business.id,
        }
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Not allowed: creating a Manager employee
        data["email"] = "manager2@example.com"
        data["role"] = "Manager"
        data["phone"] = "912345610"
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_employee_by_sales_user_forbidden(self):
        """
        A Sales role user cannot create any employee.
        """
        url = reverse("employee-list")
        headers = self.get_auth_headers(self.sales_user)
        data = {
            "email": "sales3@example.com",
            "first_name": "Sales",
            "last_name": "Three",
            "phone": "912345611",
            "password": "salespass3",
            "role": "Sales",
            "created_by": self.sales_user.id,
            "business": self.business.id,
        }
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_employee_without_business_fails(self):
        """
        If no business is provided, creation should fail.
        """
        url = reverse("employee-list")
        data = {
            "email": "nobiz@example.com",
            "first_name": "No",
            "last_name": "Biz",
            "phone": "912345612",
            "password": "nopass",
            "role": "Sales",
            "created_by": self.owner_user.id,
        }
        headers = self.get_auth_headers(self.owner_user)
        response = self.client.post(url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ----- Update Tests -----
    def test_creator_can_update_employee_with_valid_role_change(self):
        """
        A creator (with Admin role) can update an employee's role within allowed range.
        For an Admin creator, allowed role changes are to Manager or Sales.
        """
        # First, create an employee with Sales role by admin_employee_creator.
        create_url = reverse("employee-list")
        data = {
            "email": "update1@example.com",
            "first_name": "Update",
            "last_name": "One",
            "phone": "912345613",
            "password": "updatepass1",
            "role": "Sales",
            "created_by": self.admin_employee_creator.id,
            "business": self.business.id,
        }
        headers = self.get_auth_headers(self.admin_employee_creator)
        response = self.client.post(create_url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_id = response.data.get("id")
        detail_url = reverse("employee-detail", args=[employee_id])

        # Now update role from Sales to Manager (allowed)
        update_data = {"role": "Manager"}
        response = self.client.patch(detail_url, update_data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("role"), "Manager")

    def test_creator_cannot_upgrade_role_outside_allowed_range(self):
        """
        A creator with Manager role cannot upgrade an employee. Only Sales allowed.
        """
        # Create an employee with Sales role by manager_employee_creator.
        create_url = reverse("employee-list")
        data = {
            "email": "update2@example.com",
            "first_name": "Update",
            "last_name": "Two",
            "phone": "912345614",
            "password": "updatepass2",
            "role": "Sales",
            "created_by": self.manager_employee_creator.id,
            "business": self.business.id,
        }
        headers = self.get_auth_headers(self.manager_employee_creator)
        response = self.client.post(create_url, data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_id = response.data.get("id")
        detail_url = reverse("employee-detail", args=[employee_id])

        # Try to update role from Sales to Manager (not allowed for Manager creators)
        update_data = {"role": "Manager"}
        response = self.client.patch(detail_url, update_data, format="json", **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_creator_non_owner_non_admin_cannot_update_employee(self):
        """
        A user who is not the creator, business owner, or admin should not be able to update an employee.
        """
        # Create an employee by the admin employee creator.
        create_url = reverse("employee-list")
        data = {
            "email": "update3@example.com",
            "first_name": "Update",
            "last_name": "Three",
            "phone": "912345615",
            "password": "updatepass3",
            "role": "Sales",
            "created_by": self.admin_employee_creator.id,
            "business": self.business.id,
        }
        headers_creator = self.get_auth_headers(self.admin_employee_creator)
        response = self.client.post(create_url, data, format="json", **headers_creator)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_id = response.data.get("id")
        detail_url = reverse("employee-detail", args=[employee_id])

        # Attempt update by a regular user (not creator, owner, or admin)
        headers_regular = self.get_auth_headers(self.regular_user)
        update_data = {"first_name": "Hacker"}
        response = self.client.patch(
            detail_url, update_data, format="json", **headers_regular
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ----- Delete Tests -----
    def test_owner_can_delete_employee(self):
        """
        Business owner can delete an employee.
        """
        # Create an employee by admin_employee_creator.
        create_url = reverse("employee-list")
        data = {
            "email": "delete1@example.com",
            "first_name": "Delete",
            "last_name": "One",
            "phone": "912345616",
            "password": "deletepass1",
            "role": "Sales",
            "created_by": self.admin_employee_creator.id,
            "business": self.business.id,
        }
        headers_creator = self.get_auth_headers(self.admin_employee_creator)
        response = self.client.post(create_url, data, format="json", **headers_creator)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_id = response.data.get("id")
        detail_url = reverse("employee-detail", args=[employee_id])

        # Delete with business owner credentials
        headers_owner = self.get_auth_headers(self.owner_user)
        response = self.client.delete(detail_url, **headers_owner)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Employee.objects.filter(id=employee_id).exists())

    def test_admin_role_can_delete_employee(self):
        """
        An employee with Admin role (or system admin) can delete an employee.
        """
        # Create an employee by manager_employee_creator.
        create_url = reverse("employee-list")
        data = {
            "email": "delete2@example.com",
            "first_name": "Delete",
            "last_name": "Two",
            "phone": "912345617",
            "password": "deletepass2",
            "role": "Sales",
            "created_by": self.manager_employee_creator.id,
            "business": self.business.id,
        }
        headers_creator = self.get_auth_headers(self.manager_employee_creator)
        response = self.client.post(create_url, data, format="json", **headers_creator)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_id = response.data.get("id")
        detail_url = reverse("employee-detail", args=[employee_id])

        # Delete with an Admin role user (admin_employee_creator)
        headers_admin = self.get_auth_headers(self.admin_employee_creator)
        response = self.client.delete(detail_url, **headers_admin)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Employee.objects.filter(id=employee_id).exists())

    def test_non_authorized_user_cannot_delete_employee(self):
        """
        A creator (if not business owner or Admin) cannot delete an employee.
        """
        # Create an employee by manager_employee_creator.
        create_url = reverse("employee-list")
        data = {
            "email": "delete3@example.com",
            "first_name": "Delete",
            "last_name": "Three",
            "phone": "912345618",
            "password": "deletepass3",
            "role": "Sales",
            "created_by": self.manager_employee_creator.id,
            "business": self.business.id,
        }
        headers_creator = self.get_auth_headers(self.manager_employee_creator)
        response = self.client.post(create_url, data, format="json", **headers_creator)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee_id = response.data.get("id")
        detail_url = reverse("employee-detail", args=[employee_id])

        # Attempt deletion by the creator (Manager) who is not allowed to delete
        headers_manager = self.get_auth_headers(self.manager_employee_creator)
        response = self.client.delete(detail_url, **headers_manager)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Employee.objects.filter(id=employee_id).exists())

    def test_admin_can_retrieve_manager_and_sales(self):
        """
        An Admin employee can retrieve Manager and Sales employees.
        """
        create_url = reverse("employee-list")
        headers_admin = self.get_auth_headers(self.admin_employee_creator)
        # Create a Manager employee using admin_employee_creator.
        manager_data = {
            "email": "newmanager@example.com",
            "first_name": "New",
            "last_name": "Manager",
            "phone": "912345620",
            "password": "managerpassnew",
            "role": "Manager",
            "created_by": self.admin_employee_creator.id,
            "business": self.business.id,
        }
        response_manager = self.client.post(
            create_url, manager_data, format="json", **headers_admin
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)
        manager_id = response_manager.data.get("id")

        # Create a Sales employee using admin_employee_creator.
        sales_data = {
            "email": "newsales@example.com",
            "first_name": "New",
            "last_name": "Sales",
            "phone": "912345621",
            "password": "salespassnew",
            "role": "Sales",
            "created_by": self.admin_employee_creator.id,
            "business": self.business.id,
        }
        response_sales = self.client.post(
            create_url, sales_data, format="json", **headers_admin
        )
        self.assertEqual(response_sales.status_code, status.HTTP_201_CREATED)
        sales_id = response_sales.data.get("id")

        # Admin retrieves the Manager
        url_manager = reverse("employee-detail", args=[manager_id])
        response = self.client.get(url_manager, **headers_admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin retrieves the Sales
        url_sales = reverse("employee-detail", args=[sales_id])
        response = self.client.get(url_sales, **headers_admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_retrieve_sales_but_not_admin(self):
        """
        A Manager can retrieve a Sales employee but not an Admin employee.
        """
        create_url = reverse("employee-list")
        headers_manager = self.get_auth_headers(self.manager_employee_creator)
        headers_admin = self.get_auth_headers(self.admin_employee_creator)
        headers_owner = self.get_auth_headers(self.owner_user)

        # Create a Sales employee using admin_employee_creator.
        sales_data = {
            "email": "managercreatesales@example.com",
            "first_name": "Manager",
            "last_name": "Createsales",
            "phone": "912345622",
            "password": "salespassmgr",
            "role": "Sales",
            "created_by": self.admin_employee_creator.id,
            "business": self.business.id,
        }
        response_sales = self.client.post(
            create_url, sales_data, format="json", **headers_admin
        )
        self.assertEqual(response_sales.status_code, status.HTTP_201_CREATED)
        sales_id = response_sales.data.get("id")

        # Create an Admin employee using admin_employee_creator.
        admin_data = {
            "email": "newadmin@example.com",
            "first_name": "New",
            "last_name": "Admin",
            "phone": "912345623",
            "password": "adminpassnew",
            "role": "Admin",
            "created_by": self.admin_employee_creator.id,
            "business": self.business.id,
        }
        response_admin = self.client.post(
            create_url, admin_data, format="json", **headers_owner
        )
        self.assertEqual(response_admin.status_code, status.HTTP_201_CREATED)
        admin_id = response_admin.data.get("id")

        # Manager retrieves the Sales employee (allowed)
        url_sales = reverse("employee-detail", args=[sales_id])
        response = self.client.get(url_sales, **headers_manager)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Manager retrieves the Admin employee (not allowed)
        url_admin = reverse("employee-detail", args=[admin_id])
        response = self.client.get(url_admin, **headers_manager)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sales_can_only_retrieve_self(self):
        """
        A Sales employee can only retrieve his own record.
        """
        headers_sales = self.get_auth_headers(self.sales_user)
        # Sales user retrieving his own account (allowed)
        url_self = reverse("employee-detail", args=[self.sales_user.id])
        response = self.client.get(url_self, **headers_sales)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Create another Sales employee using admin_employee_creator.
        create_url = reverse("employee-list")
        sales_data = {
            "email": "othersales@example.com",
            "first_name": "Other",
            "last_name": "Sales",
            "phone": "912345624",
            "password": "othersalespass",
            "role": "Sales",
            "created_by": self.admin_employee_creator.id,
            "business": self.business.id,
        }
        headers_admin = self.get_auth_headers(self.admin_employee_creator)
        response_other = self.client.post(
            create_url, sales_data, format="json", **headers_admin
        )
        self.assertEqual(response_other.status_code, status.HTTP_201_CREATED)
        other_sales_id = response_other.data.get("id")

        # Sales user trying to retrieve another Sales employee (not allowed)
        url_other_sales = reverse("employee-detail", args=[other_sales_id])
        response = self.client.get(url_other_sales, **headers_sales)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
