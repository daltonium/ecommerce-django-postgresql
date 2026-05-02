from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum

from orders.models import Order, OrderItem
from products.models import Product


def get_seller_dashboard(seller):
    """
    Returns revenue, order count, product count, and top products.

    TWO BUGS FIXED HERE vs the previous version:
    1. F("price") → F("price_at_purchase")
       Your OrderItem model stores the price snapshot in a field named
       price_at_purchase (confirmed by the FieldError in the traceback:
       "Choices are: created_at, id, order, order_id, price_at_purchase,
       product, product_id, quantity, updated_at").
       F("price") tried to reference a field that does not exist.

    2. ExpressionWrapper is now imported at the top of this file.
       Previously it was used but never imported → NameError.
    """
    paid_items = OrderItem.objects.filter(
        product__seller=seller,
        order__status=Order.Status.PAID,
    )

    # price_at_purchase = the price that was snapshotted when the order was placed.
    # WHY snapshot? If the seller later changes the product price, the order total
    # must still reflect what the buyer actually paid — not the new price.
    revenue_expr = ExpressionWrapper(
        F("price_at_purchase") * F("quantity"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    total_revenue = paid_items.aggregate(
        total=Sum(revenue_expr)
    )["total"] or Decimal("0.00")

    total_orders = Order.objects.filter(
        items__product__seller=seller,
        status=Order.Status.PAID,
    ).distinct().count()

    total_products = Product.objects.filter(seller=seller).count()

    top_products_qs = paid_items.values(
        "product_id",
        "product__name",
    ).annotate(
        quantity_sold=Sum("quantity"),
        revenue=Sum(revenue_expr),
        orders_count=Count("order", distinct=True),
    ).order_by("-quantity_sold", "-revenue")[:5]

    top_products = [
        {
            "product_id": row["product_id"],
            "name":        row["product__name"],
            "quantity_sold": row["quantity_sold"] or 0,
            "orders_count":  row["orders_count"] or 0,
            "revenue":       str(row["revenue"] or Decimal("0.00")),
        }
        for row in top_products_qs
    ]

    return {
        "total_revenue":   str(total_revenue),
        "total_orders":    total_orders,
        "total_products":  total_products,
        "top_products":    top_products,
    }


def get_product_analytics(seller, product_id):
    """
    Per-product breakdown for a seller's own product.
    Also uses price_at_purchase for revenue calculations.
    """
    product = Product.objects.get(id=product_id, seller=seller)

    paid_items = OrderItem.objects.filter(
        product=product,
        order__status=Order.Status.PAID,
    )

    revenue_expr = ExpressionWrapper(
        F("price_at_purchase") * F("quantity"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    data = paid_items.aggregate(
        total_quantity=Sum("quantity"),
        total_revenue=Sum(revenue_expr),
        total_orders=Count("order", distinct=True),
    )

    return {
        "product_id":          product.id,
        "name":                product.name,
        "stock":               product.stock,
        "price":               str(product.price),
        "total_quantity_sold": data["total_quantity"] or 0,
        "total_revenue":       str(data["total_revenue"] or Decimal("0.00")),
        "total_orders":        data["total_orders"] or 0,
    }
