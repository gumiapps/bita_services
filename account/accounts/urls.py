from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserViewSet,
    SupplierViewSet,
    CustomerViewSet,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordChangeView,
    CustomTokenObtainPairView,
    JWTTokenVerifyView,
    api_documentation,
)

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"suppliers", SupplierViewSet)
router.register(r"customers", CustomerViewSet)

urlpatterns = [
    path("", api_documentation, name="api_documentation"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", JWTTokenVerifyView.as_view(), name="token_verify"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("password-change/", PasswordChangeView.as_view(), name="password-change"),
] + router.urls
