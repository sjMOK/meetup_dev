from rest_framework.permissions import IsAuthenticated


class UserAccessPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if super().has_permission(request, view):
            if view.action in ['list', 'create']:
                return request.user.is_admin()
            elif view.action in ['retrieve', 'partial_update', 'destroy']:
                return True

        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin():
            return True
        return obj == request.user
