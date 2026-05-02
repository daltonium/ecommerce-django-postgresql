from django.db.models import (
    Sum, Count, Avg, F, DecimalField, ExpressionWrapper
)
from django.db.models.functions import TruncMonth
from products.models import Product
from orders.models import Order, OrderItem
from reviews.models import Review


def get_seller_dashboard(seller):
    """
    Builds a complete analytics dashboard for a seller.

    annotate() vs aggregate():
    ──────────────────────────
    aggregate() = collapses ALL rows into ONE summary dict.
                  e.g., total revenue across all products → one number.
    
    annotate() = adds a computed column to EACH row in a queryset.
                 e.g., add review_count to each product row → still a list.
    
    Think of aggregate() as Excel's =SUM() at the bottom of a column.
    Think of annotate() as adding a new calculated column to each row.
    """

    # ── 1. Overall stats (aggregate = one summary) ──────────────────────────
    overall = OrderItem.objects.filter(
        order__status=Order.Status.PAID,
        product__seller=seller
    ).aggregate(
        total_revenue=Sum(
            ExpressionWrapper(
                F('price_at_purchase') * F('quantity'),
                output_field=DecimalField()
            )
            # WHY ExpressionWrapper?
            # Multiplying two fields (price × quantity) produces a
            # non-standard type. ExpressionWrapper tells Django the
            # output is a DecimalField so it generates correct SQL.
        ),
        total_orders=Count('order', distinct=True),
        # distinct=True: count unique orders, not total items.
        # Without distinct: 3 items in one order = count of 3, not 1.
        total_units_sold=Sum('quantity'),
    )

    # ── 2. Product-level stats (annotate = per-product columns) ─────────────
    products = Product.objects.filter(seller=seller).annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating'),
        # reviews__rating = traverse the reverse FK → Review model → rating field
        # Avg() computes the SQL: AVG(reviews.rating) GROUP BY product.id
        units_sold=Sum(
            'order_items__quantity',
            filter=models.Q(order_items__order__status=Order.Status.PAID)
            # filter= inside aggregate = SQL CASE WHEN → conditional aggregation.
            # Only sum quantities from PAID orders, not PENDING or CANCELLED.
        ),
        revenue=Sum(
            ExpressionWrapper(
                F('order_items__price_at_purchase') * F('order_items__quantity'),
                output_field=DecimalField()
            ),
            filter=models.Q(order_items__order__status=Order.Status.PAID)
        )
    ).order_by('-revenue')

    # ── 3. Monthly revenue trend (TruncMonth groups by month) ───────────────
    monthly_revenue = OrderItem.objects.filter(
        order__status=Order.Status.PAID,
        product__seller=seller
    ).annotate(
        month=TruncMonth('order__created_at')
        # TruncMonth = truncates a datetime to just the month.
        # 2026-03-15 → 2026-03-01 (all days in March become March 1st)
        # This groups all March orders under one "month" label.
    ).values('month').annotate(
        revenue=Sum(
            ExpressionWrapper(
                F('price_at_purchase') * F('quantity'),
                output_field=DecimalField()
            )
        )
    ).order_by('month')
    # The SQL this generates:
    # SELECT DATE_TRUNC('month', orders.created_at) AS month,
    #        SUM(price_at_purchase * quantity) AS revenue
    # FROM order_items
    # JOIN orders ON ...
    # WHERE orders.status = 'PAID' AND products.seller_id = X
    # GROUP BY month
    # ORDER BY month

    # ── 4. Recent orders ─────────────────────────────────────────────────────
    recent_orders = Order.objects.filter(
        items__product__seller=seller,
        status=Order.Status.PAID
    ).distinct().select_related('user').order_by('-created_at')[:10]
    # [:10] = LIMIT 10 in SQL — only fetch last 10 orders.
    # .distinct() = a seller with 3 items in one order shouldn't see it 3 times.

    return {
        'overall': overall,
        'products': products,
        'monthly_revenue': list(monthly_revenue),
        'recent_orders': recent_orders,
    }


def get_product_analytics(seller, product_id):
    """Deep analytics for a single product."""
    import django.db.models as models

    try:
        product = Product.objects.get(id=product_id, seller=seller)
    except Product.DoesNotExist:
        raise ValueError("Product not found.")

    stats = Review.objects.filter(product=product).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
        five_star=Count('id', filter=models.Q(rating=5)),
        four_star=Count('id', filter=models.Q(rating=4)),
        three_star=Count('id', filter=models.Q(rating=3)),
        two_star=Count('id', filter=models.Q(rating=2)),
        one_star=Count('id', filter=models.Q(rating=1)),
        # Conditional Count: COUNT(id) WHERE rating = 5
        # This builds a rating distribution in ONE query.
    )

    return {'product': product, 'review_stats': stats}