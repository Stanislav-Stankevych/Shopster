from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Allow read-only access for any user, write access for staff.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsReviewAuthorOrStaff(BasePermission):
    """
    Allow modifications on reviews for the author or staff, keep reads open.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user and request.user.is_staff:
            return True
        return request.user and obj.user_id == request.user.id
