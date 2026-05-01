from django.db import models
from django.conf import settings
from core.models import TimeStampedModel
from products.models import Product


class Cart(TimeStampedModel):
    """
    WHY OneToOneField and not ForeignKey here?
    ──────────────────────────────────────────
    ForeignKey = one user CAN HAVE many carts (1→many)
    OneToOneField = one user HAS EXACTLY one cart (1→1)

    A shopping cart is personal and singular. OneToOneField enforces
    this at the database level — a second cart for the same user would
    throw an IntegrityError. It also lets you do user.cart directly
    instead of user.carts.first() (which is fragile).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
        # related_name='cart' → user.cart gives the cart directly (not a queryset)
    )

    def __str__(self):
        return f"Cart of {self.user.email}"

    @property
    def total_price(self):
        """
        @property = makes this a computed attribute, not a stored DB column.
        Calling cart.total_price runs this function every time.
        WHY not store it? Because it changes every time items change.
        Computed = always accurate. Stored = can go stale.
        """
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(TimeStampedModel):
    """
    Junction table between Cart and Product.
    One CartItem = one product line in the cart with a quantity.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
        # related_name='items' → cart.items.all() gives all items in the cart
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # unique_together enforces at DB level: a cart cannot have
        # TWO separate rows for the same product. Instead of duplicates,
        # we UPDATE the quantity. This is the merge logic.
        unique_together = ('cart', 'product')

    @property
    def subtotal(self):
        # price * quantity for this line item
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"