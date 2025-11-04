from django.urls import path
from .views import (
    DefiListView, DefiDetailView, JoinDefiView, LeaveDefiView, UpdateProgressView,
)

app_name = 'defis'

urlpatterns = [
    # Front office: read-only views
    path('', DefiListView.as_view(), name='list'),
    path('<int:pk>/', DefiDetailView.as_view(), name='detail'),
    path('<int:pk>/join/', JoinDefiView.as_view(), name='join'),
    path('<int:pk>/leave/', LeaveDefiView.as_view(), name='leave'),
    path('<int:pk>/update-progress/', UpdateProgressView.as_view(), name='update_progress'),
]
