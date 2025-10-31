from django.urls import path
from .views import AIQueryView
from .test_views import test_ai_view

app_name = 'ai_service'

urlpatterns = [
    path('query/', AIQueryView.as_view(), name='ai-query'),
    path('test/', test_ai_view, name='ai-test'),
]
