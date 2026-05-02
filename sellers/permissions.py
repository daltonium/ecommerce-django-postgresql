from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    """
    Custom DRF permission — allows access only to authenticated sellers.

    WHY a custom permission class and not just check in the view?
    DRY principle. Instead of writing:
        if not request.user.is_authenticated or not request.user.is_seller:
            return Response(status=403)
    at the top of every seller view, we declare it once here and
    attach it with: permission_classes = [IsSeller]

    DRF calls has_permission() automatically before any view method
    (get, post, patch) runs. If it returns False, DRF returns 403
    without your view code ever executing.

    WHY check is_authenticated separately from is_seller?
    request.user can be an AnonymousUser object (not None) for
    unauthenticated requests. Calling .is_seller on AnonymousUser
    would raise AttributeError. The is_authenticated check guards
    against this — short-circuit evaluation means is_seller is
    only accessed if the user is authenticated.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_seller
        )
