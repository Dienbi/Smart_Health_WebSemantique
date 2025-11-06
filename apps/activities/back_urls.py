"""
Backoffice (Admin) URLs for Activities app - Activity and ActivityLog CRUD management
"""
from django.urls import path
from .views import (
    AdminActivityListView, AdminActivityDetailView, AdminActivityCreateView,
    AdminActivityUpdateView, AdminActivityDeleteView,
    AdminActivityLogListView, AdminActivityLogDetailView, AdminActivityLogCreateView,
    AdminActivityLogUpdateView, AdminActivityLogDeleteView,
)

app_name = 'activities_admin'

urlpatterns = [
    # Activity CRUD
    path('', AdminActivityListView.as_view(), name='list'),
    path('create/', AdminActivityCreateView.as_view(), name='create'),
    path('<int:pk>/', AdminActivityDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', AdminActivityUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', AdminActivityDeleteView.as_view(), name='delete'),
    
    # ActivityLog CRUD
    path('logs/', AdminActivityLogListView.as_view(), name='log-list'),
    path('logs/create/', AdminActivityLogCreateView.as_view(), name='log-create'),
    path('logs/<int:pk>/', AdminActivityLogDetailView.as_view(), name='log-detail'),
    path('logs/<int:pk>/edit/', AdminActivityLogUpdateView.as_view(), name='log-edit'),
    path('logs/<int:pk>/delete/', AdminActivityLogDeleteView.as_view(), name='log-delete'),
]

