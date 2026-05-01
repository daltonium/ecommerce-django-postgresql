from django.db import transaction
from django.db.models import F
from .models import Order, OrderItem
from cart.services import get_or_create_cart, clear_cart
from products.models import Product


@transaction.atomic
def create_order(user, shipping_address=''):
    """
    The full checkout flow in one atomic transaction.

    WHAT IS @transaction.atomic?
    ────────────────────────────
    Everything inside this function runs as ONE database transaction.
    Either ALL steps succeed and get committed, OR any failure
    triggers a ROLLBACK — all changes are undone as if nothing happened.

    Without atomic:
    1. Stock decremented for item 1 ✅
    2. Stock decremented for item 2 ✅
    3. Order creation fails 💥
    → You've decremented stock but no order exists. Data is corrupted.

    With atomic:
    1. Stock decremented for item 1 ✅
    2. Stock decremented for item 2 ✅
    3. Order creation fails 💥
    → ROLLBACK. Stock is restored. Cart is untouched. Clean state.
    """

    cart = get_or_create_cart(user)
    cart_items = cart.items.select_related('product').all()

    if not cart_items.exists():
        raise ValueError("Your cart is empty.")

    # ─── THE MOST IMPORTANT PART: select_for_update() ───────────────────────
    #
    # select_for_update() = "I am about to modify these rows.
    # Lock them so no other transaction can touch them until I'm done."
    #
    # This solves the race condition:
    # - User A calls select_for_update() → PostgreSQL locks the product rows
    # - User B calls select_for_update() → PostgreSQL makes User B WAIT
    # - User A finishes (commits or rolls back) → lock released
    # - User B proceeds with fresh, accurate stock numbers
    #
    # Without this: both users read stock=1, both decrement, stock goes to -1.
    # With this: User B waits, sees stock=0, raises "Out of stock" cleanly.
    #
    # This only works inside @transaction.atomic — the lock is held
    # until the transaction ends.
    # ─────────────────────────────────────────────────────────────────────────

    product_ids = [item.product_id for item in cart_items]
    products = Product.objects.select_for_update().filter(
        id__in=product_ids
    )
    # Create a dict for fast O(1) lookup: {product_id: product_object}
    products_map = {p.id: p for p in products}

    # ── Step 1: Validate ALL items before touching anything ──
    for cart_item in cart_items:
        product = products_map[cart_item.product_id]

        if not product.is_active:
            raise ValueError(f"'{product.name}' is no longer available.")

        if product.stock < cart_item.quantity:
            raise ValueError(
                f"Not enough stock for '{product.name}'. "
                f"Available: {product.stock}, Requested: {cart_item.quantity}"
            )

    # ── Step 2: Calculate total (using price_at_purchase snapshot) ──
    total_amount = sum(
        products_map[item.product_id].price * item.quantity
        for item in cart_items
    )

    # ── Step 3: Create the Order ──
    order = Order.objects.create(
        user=user,
        status=Order.Status.PENDING,
        total_amount=total_amount,
        shipping_address=shipping_address
    )

    # ── Step 4: Create OrderItems + Decrement Stock ──
    order_items = []
    for cart_item in cart_items:
        product = products_map[cart_item.product_id]

        order_items.append(OrderItem(
            order=order,
            product=product,
            quantity=cart_item.quantity,
            price_at_purchase=product.price   # ← snapshot the price RIGHT NOW
        ))

    # bulk_create = inserts ALL order items in ONE SQL query
    # instead of one INSERT per item. Much more efficient.
    OrderItem.objects.bulk_create(order_items)

    # ── Step 5: Decrement Stock using F() expressions ──
    for cart_item in cart_items:
        Product.objects.filter(id=cart_item.product_id).update(
            stock=F('stock') - cart_item.quantity
        )
        """
        WHY F('stock') - quantity and NOT product.stock - quantity?
        ─────────────────────────────────────────────────────────────
        product.stock is the value Python read from DB BEFORE the lock.
        Another request could have changed it in the meantime.

        F('stock') tells Django: "let PostgreSQL compute this using
        the CURRENT value in the database column right now."

        SQL generated: UPDATE products SET stock = stock - 2 WHERE id = 5
        This is atomic at the DB level — no stale value risk.
        Always use F() for counter decrements/increments.
        """

    # ── Step 6: Clear the cart ──
    clear_cart(user)

    return order


def get_user_orders(user):
    """Fetch all orders for a user with optimized queries."""
    return Order.objects.filter(
        user=user
    ).prefetch_related(
        'items',
        'items__product'
        # Prefetch items AND each item's product in 2 extra queries total.
        # Without this: N orders × M items = potentially hundreds of queries.
    ).order_by('-created_at')


def cancel_order(user, order_id):
    """Cancel a PENDING order and restore stock."""
    try:
        order = Order.objects.get(id=order_id, user=user)
    except Order.DoesNotExist:
        raise ValueError("Order not found.")

    if order.status != Order.Status.PENDING:
        raise ValueError(
            f"Cannot cancel an order with status '{order.status}'. "
            "Only PENDING orders can be cancelled."
        )

    with transaction.atomic():
        # Restore stock for each item
        for item in order.items.select_related('product'):
            Product.objects.filter(id=item.product_id).update(
                stock=F('stock') + item.quantity
                # Same F() pattern — restore using DB-level arithmetic
            )
        order.status = Order.Status.CANCELLED
        order.save()

    return order