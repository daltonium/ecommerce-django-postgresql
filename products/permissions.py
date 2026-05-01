from rest_framework.permissions import BasePermission


class IsSeller(BasePermission):
    """
    Custom permission: only users with is_seller=True can access this view.

    WHY create a custom permission instead of checking in the view?
    ───────────────────────────────────────────────────────────────
    If you check `if not request.user.is_seller: return 403` inside every view,
    you repeat that logic everywhere. A permission class is reusable —
    attach it to any view with one line: permission_classes = [IsSeller]
    """

    message = 'Only sellers can perform this action.'
    # 'message' = the error text returned when permission is denied

    def has_permission(self, request, view):
        # has_permission() = called on every request to this view
        return request.user.is_authenticated and request.user.is_seller


class IsSellerOrReadOnly(BasePermission):
    """
    Read (GET, HEAD, OPTIONS) = anyone.
    Write (POST, PUT, PATCH, DELETE) = sellers only.
    This is perfect for the product catalog:
    - Buyers can browse products
    - Only sellers can create/edit/delete
    """

    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
    # SAFE_METHODS = HTTP verbs that don't change data

    def has_permission(self, request, view):
        if request.method in self.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_seller

    def has_object_permission(self, request, view, obj):
        # has_object_permission() = called when accessing a SPECIFIC object (e.g., /products/5/)
        # This prevents a seller from editing ANOTHER seller's product.
        if request.method in self.SAFE_METHODS:
            return True
        return obj.seller == request.user
        # obj.seller = the product's owner. request.user = the person making the request.
        # Only the product's own seller can modify it.