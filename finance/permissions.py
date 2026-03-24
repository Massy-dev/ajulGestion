from rest_framework.permissions import BasePermission


class IsTreasurerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        print('**************** ',request.user.role)
        return request.user.is_authenticated and (
            request.user.role in ["Admin", "Trésorié"]
        )


class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"
