from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HealthRecordViewSet, HealthMetricViewSet,
    StudentHealthRecordViewSet, TeacherHealthRecordViewSet,
    health_record_list_view
)

router = DefaultRouter()
router.register(r'records', HealthRecordViewSet, basename='healthrecord')
router.register(r'metrics', HealthMetricViewSet, basename='healthmetric')
router.register(r'student-records', StudentHealthRecordViewSet, basename='studenthealthrecord')
router.register(r'teacher-records', TeacherHealthRecordViewSet, basename='teacherhealthrecord')

app_name = 'health_records'

urlpatterns = [
    # Web interface URLs
    path('', health_record_list_view, name='record-list'),
    
    # API URLs
    path('api/', include(router.urls)),
]
