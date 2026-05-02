import cohere
from django.conf import settings
from django.db.models import Avg
from .models import ChatSession, ChatMessage
from products.models import Product
from orders.models import Order

co = cohere.Client(settings.COHERE_API_KEY)
# Initialize once — reused across all requests (same as razorpay_client in Phase 7)


def get_or_create_session(user):
    """Get the user's active chat session, or create a fresh one."""
    session, created = ChatSession.objects.get_or_create(
        user=user,
        is_active=True
    )
    return session


def build_system_prompt(user):
    """
    WHAT IS A SYSTEM PROMPT?
    ─────────────────────────
    A system prompt is a hidden instruction given to the AI BEFORE
    any user message. It defines the AI's personality, role, and
    what context it has access to.

    The AI will stay in character and use this context to answer.
    This is how you make a generic AI model into "BlueCart Assistant."
    """

    # Fetch relevant context from YOUR database
    products = Product.objects.filter(is_active=True).select_related(
        'category', 'seller'
    ).annotate(avg_rating=Avg('reviews__rating'))[:20]
    # Limit to 20 — sending 1000 products to the API wastes tokens and money.
    # In production, you'd use semantic search to find the most relevant products.

    product_lines = []
    for p in products:
        rating = f"{p.avg_rating:.1f}★" if p.avg_rating else "No ratings"
        product_lines.append(
            f"- {p.name} | ₹{p.price} | Stock: {p.stock} | "
            f"Category: {p.category.name if p.category else 'N/A'} | {rating}"
        )

    products_context = "\n".join(product_lines) if product_lines else "No products available."

    # Fetch user's order history for personalized responses
    recent_orders = Order.objects.filter(
        user=user
    ).prefetch_related('items__product').order_by('-created_at')[:5]

    order_lines = []
    for order in recent_orders:
        items = ", ".join([f"{i.product.name} (×{i.quantity})" for i in order.items.all()])
        order_lines.append(f"- Order #{order.id}: {items} | Status: {order.status} | ₹{order.total_amount}")

    orders_context = "\n".join(order_lines) if order_lines else "No orders yet."

    return f"""You are BlueCart Assistant, a helpful AI for the BlueCart e-commerce platform.
You help users find products, track orders, and answer shopping questions.
Be friendly, concise, and helpful. Always respond in the same language the user writes in.

AVAILABLE PRODUCTS:
{products_context}

USER'S RECENT ORDERS:
{orders_context}

RULES:
- Only recommend products from the list above.
- If a product is out of stock (Stock: 0), say so clearly.
- For order status questions, refer to the user's order history above.
- If asked something outside shopping/orders, politely redirect to BlueCart topics.
- Keep responses under 150 words unless a detailed explanation is needed.
- Format prices in Indian Rupees (₹).
"""


def build_chat_history(session):
    """
    Convert our DB messages into Cohere's expected format.

    WHY convert? Cohere expects this exact structure:
    [
        {"role": "USER", "message": "..."},
        {"role": "CHATBOT", "message": "..."},
    ]
    Our DB stores the same data — we just reshape it.
    We send the last 10 messages to keep the context window manageable.
    Sending too much history = slower responses + higher token usage.
    """
    messages = session.messages.order_by('-created_at')[:10]
    # Get last 10, then reverse to chronological order
    messages = list(reversed(messages))

    return [
        {"role": msg.role, "message": msg.content}
        for msg in messages
    ]


def chat(user, user_message):
    """
    Main chat function — orchestrates the full request/response cycle.
    """
    session = get_or_create_session(user)

    # Save the user's message to DB first
    ChatMessage.objects.create(
        session=session,
        role=ChatMessage.Role.USER,
        content=user_message
    )

    # Build context
    system_prompt = build_system_prompt(user)
    chat_history = build_chat_history(session)

    try:
        response = co.chat(
            message=user_message,
            # The current message from the user

            model='command-r',
            # command-r = Cohere's model optimized for RAG and conversation.
            # Free tier supports this model. 'command-r-plus' is more capable
            # but uses more tokens.

            preamble=system_prompt,
            # preamble = Cohere's term for system prompt.
            # Injected before all conversation history.

            chat_history=chat_history,
            # The conversation so far — gives the AI memory of this session.

            temperature=0.3,
            # temperature controls randomness:
            # 0.0 = deterministic, always same answer
            # 1.0 = very creative/random
            # 0.3 = slightly creative but mostly factual — good for shopping assistant
        )

        ai_reply = response.text

    except Exception as e:
        # Never let an API failure crash your app — degrade gracefully
        ai_reply = (
            "I'm having trouble connecting right now. "
            "Please try again in a moment, or contact support."
        )

    # Save the AI's reply to DB
    ChatMessage.objects.create(
        session=session,
        role=ChatMessage.Role.CHATBOT,
        content=ai_reply
    )

    return {
        'reply': ai_reply,
        'session_id': session.id
    }


def clear_session(user):
    """Start a fresh conversation — close the current session."""
    ChatSession.objects.filter(user=user, is_active=True).update(is_active=False)
    # Creates a new session on next chat() call automatically