from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission

#Permission Classes Testing ...
class ViewByStaffOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        print('insidnde has permission', request.user)
        user = request.user
        if request.method == 'GET' or 'POST' or request.method == 'PUT' or request.method == 'DELETE':
            if user.is_staff:
                return True
        return False