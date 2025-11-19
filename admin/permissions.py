from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Permission class to check if user is both staff AND superuser.
    """
    message = 'You must be both staff and superuser to access this resource.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return user.is_staff and user.is_superuser

