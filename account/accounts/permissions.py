from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "created_by"):
            return obj.created_by == request.user or request.user.is_staff
        return obj == request.user or request.user.is_staff
