from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class Category(TimeStampedModel):
    """
    WHY a separate Category model instead of a CharField?
    ──────────────────────────────────────────────────────
    A CharField like category='Electronics' means:
    - Typos create duplicates ("Electronics" vs "electronics")
    - Renaming a category requires updating thousands of rows
    - You can't attach extra data (description, image) to a category

    A separate model = one source of truth. All products just point to it.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    # SlugField = URL-friendly version of name. "Smart Phones" → "smart-phones"
    # Used in URLs: /products/category/smart-phones/ instead of /products/category/3/
    # Human-readable URLs are better for SEO and users.

    description = models.TextField(blank=True)
    # blank=True means this field is OPTIONAL in forms/serializers.
    # null=True (not used here) means the DB column can store NULL.
    # For text fields, prefer blank=True with default='' over null=True —
    # two ways to represent "empty" (NULL vs '') creates ambiguity.

    class Meta:
        verbose_name_plural = 'Categories'
        # WHY: Django auto-generates "Categorys" in admin. This fixes it.
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    """
    Core product table. Notice it inherits created_at + updated_at
    from TimeStampedModel — the payoff from Phase 2!
    """
    name = models.CharField(max_length=255)

    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    # WHY DecimalField and NOT FloatField for money?
    # FloatField uses binary floating point — it CANNOT represent
    # values like 0.1 exactly. 0.1 + 0.2 = 0.30000000000000004
    # DecimalField uses exact decimal arithmetic. For money, always DecimalField.

    stock = models.PositiveIntegerField(default=0)
    # PositiveIntegerField = enforces stock >= 0 at the DB level.

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products'
        # ForeignKey = "many products belong to one seller"
        # on_delete=CASCADE = if the seller is deleted, delete their products too.
        # related_name='products' = lets you do seller.products.all() from a User object.
        # settings.AUTH_USER_MODEL is always the right way to reference the User model.
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
        # on_delete=SET_NULL = if a category is deleted, products stay but category→NULL.
        # WHY not CASCADE here? Deleting "Electronics" shouldn't delete all phones!
    )

    is_active = models.BooleanField(default=True)
    # Sellers can "soft delete" a product — hide it without destroying the data.
    # Orders that reference this product still have valid history.

    class Meta:
        ordering = ['-created_at']
        # Newest products first by default.

        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['seller']),
            models.Index(fields=['is_active']),
            # WHY indexes?
            # Without an index, PostgreSQL scans EVERY row to find matches (O(n)).
            # With an index, it uses a B-tree structure to find rows in O(log n).
            # Rule of thumb: index any field you filter or order by frequently.
            # name → for search; category/seller → for filtering; is_active → filtered on every query.
        ]

    def __str__(self):
        return self.name


class ProductImage(TimeStampedModel):
    """
    WHY a separate ProductImage model instead of one ImageField on Product?
    ────────────────────────────────────────────────────────────────────────
    One product can have multiple images (front, back, detail shots).
    A single ImageField can only store one. A related model stores unlimited.
    This is a classic one-to-many relationship.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
        # related_name='images' → product.images.all() gives all images for a product
    )
    image = models.ImageField(upload_to='products/')
    # upload_to='products/' = files saved to MEDIA_ROOT/products/
    # ImageField requires Pillow (already installed in Phase 1).

    is_primary = models.BooleanField(default=False)
    # Marks the main display image for listing pages.

    def __str__(self):
        return f"Image for {self.product.name}"