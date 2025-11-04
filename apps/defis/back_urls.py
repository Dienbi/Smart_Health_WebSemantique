from django.urls import path
from .views import (
    AdminDefiListView, AdminDefiDetailView,
    AdminDefiCreateView, AdminDefiUpdateView, AdminDefiDeleteView,
)

app_name = 'defis_admin'

urlpatterns = [
    path('', AdminDefiListView.as_view(), name='list'),
    path('create/', AdminDefiCreateView.as_view(), name='create'),
    path('<int:pk>/', AdminDefiDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', AdminDefiUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', AdminDefiDeleteView.as_view(), name='delete'),
]
