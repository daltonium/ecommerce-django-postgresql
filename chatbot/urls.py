from django.urls import path
from .views import ChatView, ClearChatView

urlpatterns = [
    path('chatbot/', ChatView.as_view(), name='chatbot'),
    path('chatbot/clear/', ClearChatView.as_view(), name='chatbot-clear'),
]