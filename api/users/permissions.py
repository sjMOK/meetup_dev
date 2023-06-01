from rest_framework import permissions
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class UserAccessPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if view.action == "create":
                return request.user.is_admin()
            else:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin():
            return True
        return obj == request.user


class IsNonAdminUser(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and not request.user.is_admin()


class IsAdminUser(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_admin()


class IsAdminOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return request.user.is_admin()


class IsOwnerOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.auth_id == request.user


class IsOwnerOrAdmin(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        # Instance must have an attribute named `owner`.
        return obj.booker == request.user or request.user.is_admin()
