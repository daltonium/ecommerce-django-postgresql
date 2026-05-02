"""
ASGI config for bluecart project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""


import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluecart.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    # 'http' = regular Django handles all HTTP requests as before

    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
    # 'websocket' = WebSocket requests go to URLRouter → ChatConsumer
    # AuthMiddlewareStack: reads the session/token and populates
    # scope['user'] — same as request.user in regular views.
})

# ProtocolTypeRouter = the traffic cop.
# It inspects every incoming connection and routes it:
# - Is it HTTP? → Django handles it normally
# - Is it WebSocket? → Channels handles it