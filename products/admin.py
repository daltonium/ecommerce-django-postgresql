from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    """
    Inline = shows ProductImages INSIDE the Product admin page.
    You can add/remove images without leaving the product form.
    TabularInline = displays them in a compact table layout.
    """
    model = ProductImage
    extra = 1  # Show 1 empty extra form slot for adding a new image


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'seller', 'category', 'is_active', 'created_at']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'description']
    inlines = [ProductImageInline]
    # list_filter adds a sidebar filter panel in admin.
    # search_fields adds a search box that queries these fields.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    # prepopulated_fields: as you type the category name,
    # the slug field auto-fills with a URL-safe version. Pure convenience.