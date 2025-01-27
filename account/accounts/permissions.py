from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff
