"""
WHY a services.py file?
────────────────────────
Business logic doesn't belong in views (they should be thin) or models (they should only know about their own data).

A service layer holds complex operations that coordinate multiple models. It's reusable — any view or future task can call it.
This is the Service Layer pattern.
"""

from django.db import transaction
from .models import Cart, CartItem
from products.models import Product


def get_or_create_cart(user):
    """
    get_or_create() is a Django ORM shortcut:
    - Tries to GET an existing cart for this user
    - If none exists, CREATEs one
    - Returns (object, created) → created is True/False
    One DB query instead of: try/get → except → create
    """
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@transaction.atomic
def add_to_cart(user, product_id, quantity=1):
    """
    @transaction.atomic = wraps everything in a single DB transaction.
    If ANY line raises an exception, ALL changes are rolled back.
    WHY critical here? We validate stock, then update cart.
    Without atomic, a crash between those two steps = inconsistent data.
    """
    cart = get_or_create_cart(user)

    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        raise ValueError("Product not found or unavailable.")

    # Stock validation
    if product.stock < quantity:
        raise ValueError(
            f"Only {product.stock} unit(s) available. You requested {quantity}."
        )

    # get_or_create with defaults handles the MERGE logic:
    # - If this product is already in the cart → get the existing CartItem
    # - If not → create a new one with quantity=quantity
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
        # 'defaults' = only used during CREATE, not during GET.
        # If the item already exists, 'defaults' is ignored entirely.
    )

    if not created:
        # Item already existed → ADD to existing quantity (merge)
        new_quantity = cart_item.quantity + quantity

        # Re-validate stock against the new total
        if product.stock < new_quantity:
            raise ValueError(
                f"Cannot add {quantity} more. "
                f"Only {product.stock - cart_item.quantity} more unit(s) available."
            )

        cart_item.quantity = new_quantity
        cart_item.save()
        # .save() only updates the quantity field — efficient

    return cart_item


@transaction.atomic
def update_cart_item(user, product_id, quantity):
    """Update quantity of a specific item. Quantity=0 removes it."""
    cart = get_or_create_cart(user)

    try:
        cart_item = CartItem.objects.select_related('product').get(
            cart=cart,
            product_id=product_id
        )
    except CartItem.DoesNotExist:
        raise ValueError("This item is not in your cart.")

    if quantity <= 0:
        cart_item.delete()
        return None

    if cart_item.product.stock < quantity:
        raise ValueError(f"Only {cart_item.product.stock} unit(s) in stock.")

    cart_item.quantity = quantity
    cart_item.save()
    return cart_item


def remove_from_cart(user, product_id):
    """Remove a specific product from the cart entirely."""
    cart = get_or_create_cart(user)
    deleted_count, _ = CartItem.objects.filter(
        cart=cart,
        product_id=product_id
    ).delete()
    # .delete() returns (number_deleted, {model: count})
    # We check deleted_count to know if anything was actually removed.
    return deleted_count > 0


def clear_cart(user):
    """Remove ALL items from the cart (used after order is placed)."""
    cart = get_or_create_cart(user)
    cart.items.all().delete()