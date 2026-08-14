from rest_framework.permissions import BasePermission
from apps.accounts.models import User


class IsAdminRoleOrStaff(BasePermission):
    """
    Allows access only to authenticated users with ADMIN role, staff, or superuser status.
    SUPPORT and FINANCE roles also have read/limited access where applicable.
    """

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if user.is_superuser or user.is_staff:
            return True

        return user.role in [User.Role.ADMIN, User.Role.SUPPORT, User.Role.FINANCE]


class IsSuperAdminOnly(BasePermission):
    """Allows access only to Superuser or ADMIN role."""

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        return bool(user.is_superuser or user.is_staff or user.role == User.Role.ADMIN)
