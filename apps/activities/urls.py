from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityViewSet, ActivityLogViewSet,
    CardioViewSet, MusculationViewSet, NatationViewSet,
    activity_list_view, activity_detail_view
)

router = DefaultRouter()
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'logs', ActivityLogViewSet, basename='activitylog')
router.register(r'cardio', CardioViewSet, basename='cardio')
router.register(r'musculation', MusculationViewSet, basename='musculation')
router.register(r'natation', NatationViewSet, basename='natation')

app_name = 'activities'

urlpatterns = [
    # Web interface URLs
    path('', activity_list_view, name='activity-list'),
    path('<int:activity_id>/', activity_detail_view, name='activity-detail'),
    
    # API URLs
    path('api/', include(router.urls)),
]
