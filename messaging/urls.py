from django.urls import path
from .views import ConversationListView, ConversationDetailView

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversations'),
    path('conversations/<int:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),
]