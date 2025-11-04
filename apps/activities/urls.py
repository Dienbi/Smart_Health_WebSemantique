from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActivityViewSet, ActivityLogViewSet,
    CardioViewSet, MusculationViewSet, NatationViewSet
)

router = DefaultRouter()
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'logs', ActivityLogViewSet, basename='activitylog')
router.register(r'cardio', CardioViewSet, basename='cardio')
router.register(r'musculation', MusculationViewSet, basename='musculation')
router.register(r'natation', NatationViewSet, basename='natation')

urlpatterns = [
    path('', include(router.urls)),
]
