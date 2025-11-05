from django.urls import path
from .views import (
    AdminHealthMetricListView, AdminHealthMetricDetailView,
    AdminHealthMetricCreateView, AdminHealthMetricUpdateView, AdminHealthMetricDeleteView,
)

app_name = 'health_metrics_admin'

urlpatterns = [
    # Health Metrics CRUD
    path('', AdminHealthMetricListView.as_view(), name='list'),
    path('create/', AdminHealthMetricCreateView.as_view(), name='create'),
    path('<int:pk>/', AdminHealthMetricDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', AdminHealthMetricUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', AdminHealthMetricDeleteView.as_view(), name='delete'),
]

