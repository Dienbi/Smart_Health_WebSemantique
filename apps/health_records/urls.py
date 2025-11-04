from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HealthRecordViewSet, HealthMetricViewSet,
    StudentHealthRecordViewSet, TeacherHealthRecordViewSet
)

router = DefaultRouter()
router.register(r'records', HealthRecordViewSet, basename='healthrecord')
router.register(r'metrics', HealthMetricViewSet, basename='healthmetric')
router.register(r'student-records', StudentHealthRecordViewSet, basename='studenthealthrecord')
router.register(r'teacher-records', TeacherHealthRecordViewSet, basename='teacherhealthrecord')

urlpatterns = [
    path('', include(router.urls)),
]
