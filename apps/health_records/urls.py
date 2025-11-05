from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HealthRecordViewSet, HealthMetricViewSet,
    StudentHealthRecordViewSet, TeacherHealthRecordViewSet,
    health_record_list_view, health_record_create_view,
    health_record_update_view, health_record_delete_view,
    health_record_detail_view
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
    path('create/', health_record_create_view, name='record-create'),
    path('<int:record_id>/', health_record_detail_view, name='record-detail'),
    path('<int:record_id>/update/', health_record_update_view, name='record-update'),
    path('<int:record_id>/delete/', health_record_delete_view, name='record-delete'),
    
    # API URLs
    path('api/', include(router.urls)),
]
