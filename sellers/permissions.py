from rest_framework.permissions import BasePermission

class IsSeller(BasePermission):
    """
    WHY a custom permission?
    ─────────────────────────
    DRF's IsAuthenticated only checks login.
    IsSeller checks login AND that the user is a seller.
    Without this, any buyer could POST to /api/sellers/products/.
    """
    message = "You must be a seller to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_seller
        )