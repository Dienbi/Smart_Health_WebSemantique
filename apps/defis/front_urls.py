from django.urls import path
from .views import (
    DefiListView, DefiDetailView,
)

app_name = 'defis'

urlpatterns = [
    # Front office: read-only views
    path('', DefiListView.as_view(), name='list'),
    path('<int:pk>/', DefiDetailView.as_view(), name='detail'),
]
