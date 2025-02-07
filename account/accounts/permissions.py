from rest_framework.permissions import BasePermission
from .models import Business, Employee


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "created_by"):
            return obj.created_by == request.user or request.user.is_staff
        return obj == request.user or request.user.is_staff


class IsBusinessOwnerOrAdmin(BasePermission):
    """
    Custom permission that allows editing or deleting a Business only if the
    current user is the owner of the business or an admin.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff


class EmployeeCreatePermission(BasePermission):
    """
    Allow creation only if:
      - The current user is the business owner or a staff user, OR
      - The current user has role 'Admin' and is creating a 'Manager' or 'Sales', OR
      - The current user has role 'Manager' and is creating a 'Sales'.
    """

    def has_permission(self, request, view):
        if request.method != "POST":
            return True
        business_id = request.data.get("business")
        new_role = request.data.get("role")
        if not business_id or not new_role:
            return False
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            return False
        user = request.user
        if business.owner == user or user.is_staff:
            return True
        employee = Employee.objects.get(id=user.id)
        if employee.role == "Admin" and new_role in ("Manager", "Sales"):
            return True
        elif employee.role == "Manager" and new_role == "Sales":
            return True
        return False


class EmployeeUpdatePermission(BasePermission):
    """
    Allow updating if the user is the creator, business owner,
    or staff; and if updating role, enforce:
      - Business owner or staff can change to anything.
      - Otherwise, 'Admin' can change only to 'Manager' or 'Sales',
        and 'Manager' only to 'Sales'.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Allow update if user is admin, business owner, or the creator.
        if not (
            user.is_staff
            or obj.business.owner == user
            or obj.created_by == user
            or obj == user
        ):
            return False
        # If not updating role, allow.
        if "role" not in request.data:
            return True
        new_role = request.data.get("role")
        # Business owner or staff can update without extra checks.
        if obj.business.owner == user or user.is_staff:
            return True
        employee = Employee.objects.get(id=user.id)
        if employee.role == "Admin" and new_role in ("Manager", "Sales"):
            return True
        elif employee.role == "Manager" and new_role == "Sales":
            return True
        return False


class EmployeeDeletePermission(BasePermission):
    """
    Allow deletion only if the current user is the business owner,
    a staff user, or has role 'Admin'.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.business.owner == user or user.is_staff:
            return True
        employee = Employee.objects.get(id=user.id)
        if employee.role == "Admin":
            return True
        return False


class EmployeeRetrievePermission(BasePermission):
    """
    Allow retrieval if:
      - The request user is retrieving his/her own record, OR
      - The request user is the owner of the business, OR
      - The target employee has a higher role than the request user.
    Role hierarchy: Sales (1) < Manager (2) < Admin (3)
    """

    def has_object_permission(self, request, view, obj):
        # Allow self‐retrieve
        if obj.id == request.user.id:
            return True

        # Allow business owner (assuming the Employee is linked to a Business)
        if hasattr(obj, "business") and obj.business.owner == request.user:
            return True

        # Get the roles using the Employee model so that the updated role is available.
        try:
            requester = Employee.objects.get(id=request.user.id)
            target = Employee.objects.get(id=obj.id)
        except Employee.DoesNotExist:
            return False

        hierarchy = {"Sales": 1, "Manager": 2, "Admin": 3}
        if requester.role not in hierarchy or target.role not in hierarchy:
            return False

        # Allow if target has a lower role value.
        return hierarchy[target.role] < hierarchy[requester.role]


class IsNonEmployeeUser(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return not Employee.objects.filter(id=request.user.id).exists()
        return True
