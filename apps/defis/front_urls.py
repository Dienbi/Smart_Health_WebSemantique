from django.urls import path
from .views import (
    DefiListView, DefiDetailView, DefiCreateView, DefiUpdateView, DefiDeleteView
)

app_name = 'defis'

urlpatterns = [
    path('', DefiListView.as_view(), name='list'),
    path('create/', DefiCreateView.as_view(), name='create'),
    path('<int:pk>/', DefiDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', DefiUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', DefiDeleteView.as_view(), name='delete'),
]
