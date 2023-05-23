from rest_framework.permissions import IsAuthenticated


class UserAccessPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if view.action == 'create':
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
