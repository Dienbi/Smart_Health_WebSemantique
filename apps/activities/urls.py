from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityViewSet, ActivityLogViewSet,
    CardioViewSet, MusculationViewSet, NatationViewSet,
    activity_list_view, activity_create_view, activity_detail_view,
    activity_update_view, activity_delete_view,
    activity_log_list_view, activity_log_create_view, activity_log_detail_view,
    activity_log_update_view, activity_log_delete_view,
    AdminActivityListView, AdminActivityDetailView, AdminActivityCreateView,
    AdminActivityUpdateView, AdminActivityDeleteView,
    AdminActivityLogListView, AdminActivityLogDetailView, AdminActivityLogCreateView,
    AdminActivityLogUpdateView, AdminActivityLogDeleteView,
)

router = DefaultRouter()
router.register(r'activities', ActivityViewSet, basename='activity-api')
router.register(r'logs', ActivityLogViewSet, basename='activitylog-api')
router.register(r'cardio', CardioViewSet, basename='cardio-api')
router.register(r'musculation', MusculationViewSet, basename='musculation-api')
router.register(r'natation', NatationViewSet, basename='natation-api')

app_name = 'activities'

urlpatterns = [
    # Web interface URLs (Front Office - Activity CRUD) - MUST come first to take priority
    path('', activity_list_view, name='activity-list'),
    path('create/', activity_create_view, name='activity-create'),
    path('<int:activity_id>/', activity_detail_view, name='activity-detail'),
    path('<int:activity_id>/edit/', activity_update_view, name='activity-edit'),
    path('<int:activity_id>/delete/', activity_delete_view, name='activity-delete'),
    
    # Web interface URLs (Front Office - Activity Log CRUD)
    path('logs/', activity_log_list_view, name='activity-log-list'),
    path('logs/create/', activity_log_create_view, name='activity-log-create'),
    path('logs/<int:activity_log_id>/', activity_log_detail_view, name='activity-log-detail'),
    path('logs/<int:activity_log_id>/edit/', activity_log_update_view, name='activity-log-edit'),
    path('logs/<int:activity_log_id>/delete/', activity_log_delete_view, name='activity-log-delete'),
    
    # API URLs - Must come after web URLs to avoid conflicts
    path('api/', include(router.urls)),
]
