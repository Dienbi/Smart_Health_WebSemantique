from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import HealthRecord, HealthMetric, StudentHealthRecord, TeacherHealthRecord
from .serializers import (
    HealthRecordSerializer, HealthMetricSerializer,
    StudentHealthRecordSerializer, TeacherHealthRecordSerializer
)


class HealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HealthRecord model
    """
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter records by user if not staff"""
        if self.request.user.is_staff:
            return HealthRecord.objects.all()
        return HealthRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request when creating record"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_records(self, request):
        """Get records for current user"""
        records = HealthRecord.objects.filter(user=request.user)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """Get all metrics for a specific health record"""
        record = self.get_object()
        metrics = record.metrics.all()
        serializer = HealthMetricSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest health record for current user"""
        record = HealthRecord.objects.filter(user=request.user).first()
        if record:
            serializer = self.get_serializer(record)
            return Response(serializer.data)
        return Response(
            {'message': 'No health records found'},
            status=status.HTTP_404_NOT_FOUND
        )


class HealthMetricViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HealthMetric model
    """
    queryset = HealthMetric.objects.all()
    serializer_class = HealthMetricSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter metrics by user's health records if not staff"""
        if self.request.user.is_staff:
            return HealthMetric.objects.all()
        return HealthMetric.objects.filter(health_record__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_metrics(self, request):
        """Get metrics for current user"""
        metrics = HealthMetric.objects.filter(health_record__user=request.user)
        serializer = self.get_serializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get metrics by type"""
        metric_type = request.query_params.get('type', None)
        queryset = self.get_queryset()
        
        if metric_type:
            queryset = queryset.filter(metric_name__icontains=metric_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest_by_type(self, request):
        """Get latest metric of each type for current user"""
        from django.db.models import Max
        
        metric_names = HealthMetric.objects.filter(
            health_record__user=request.user
        ).values_list('metric_name', flat=True).distinct()
        
        latest_metrics = []
        for name in metric_names:
            metric = HealthMetric.objects.filter(
                health_record__user=request.user,
                metric_name=name
            ).order_by('-recorded_at').first()
            if metric:
                latest_metrics.append(metric)
        
        serializer = self.get_serializer(latest_metrics, many=True)
        return Response(serializer.data)


class StudentHealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StudentHealthRecord model
    """
    queryset = StudentHealthRecord.objects.all()
    serializer_class = StudentHealthRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return StudentHealthRecord.objects.all()
        # Students can only see their own records
        return StudentHealthRecord.objects.filter(student__user=self.request.user)


class TeacherHealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TeacherHealthRecord model
    """
    queryset = TeacherHealthRecord.objects.all()
    serializer_class = TeacherHealthRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return TeacherHealthRecord.objects.all()
        # Teachers can only see their own records
        return TeacherHealthRecord.objects.filter(teacher__user=self.request.user)


# Web Interface Views
@login_required
def health_record_list_view(request):
    """Display list of user's health records"""
    records = HealthRecord.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'health_records/record_list.html', {
        'records': records
    })
