from rest_framework import permissions


class NoDelete(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.method != 'DELETE'
