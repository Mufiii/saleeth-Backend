from rest_framework.permissions import BasePermission


class IsNotBlocked(BasePermission):
    message = 'Your account is blocked.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return not getattr(user, 'is_blocked', False)


