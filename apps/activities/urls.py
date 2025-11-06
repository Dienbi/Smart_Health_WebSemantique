from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityViewSet, ActivityLogViewSet,
    CardioViewSet, MusculationViewSet, NatationViewSet,
    activity_log_list_view, activity_log_create_view, activity_log_detail_view,
    activity_log_update_view, activity_log_delete_view,
    AdminActivityListView, AdminActivityDetailView, AdminActivityCreateView,
    AdminActivityUpdateView, AdminActivityDeleteView,
    AdminActivityLogListView, AdminActivityLogDetailView, AdminActivityLogCreateView,
    AdminActivityLogUpdateView, AdminActivityLogDeleteView,
)

router = DefaultRouter()
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'logs', ActivityLogViewSet, basename='activitylog')
router.register(r'cardio', CardioViewSet, basename='cardio')
router.register(r'musculation', MusculationViewSet, basename='musculation')
router.register(r'natation', NatationViewSet, basename='natation')

app_name = 'activities'

urlpatterns = [
    # Web interface URLs (Front Office - Activity Log CRUD)
    path('', activity_log_list_view, name='activity-log-list'),
    path('create/', activity_log_create_view, name='activity-log-create'),
    path('<int:activity_log_id>/', activity_log_detail_view, name='activity-log-detail'),
    path('<int:activity_log_id>/edit/', activity_log_update_view, name='activity-log-edit'),
    path('<int:activity_log_id>/delete/', activity_log_delete_view, name='activity-log-delete'),
    
    # API URLs
    path('api/', include(router.urls)),
]
