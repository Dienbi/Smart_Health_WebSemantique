from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Activity, ActivityLog, Cardio, Musculation, Natation
from .serializers import (
    ActivitySerializer, ActivityLogSerializer,
    CardioSerializer, MusculationSerializer, NatationSerializer
)


class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Activity model
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get all logs for a specific activity"""
        activity = self.get_object()
        logs = activity.logs.all()
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data)


class ActivityLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ActivityLog model
    """
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter logs by user if not staff"""
        if self.request.user.is_staff:
            return ActivityLog.objects.all()
        return ActivityLog.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request when creating log"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_logs(self, request):
        """Get logs for current user"""
        logs = ActivityLog.objects.filter(user=request.user)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_intensity(self, request):
        """Get logs grouped by intensity"""
        intensity = request.query_params.get('intensity', None)
        if intensity:
            logs = ActivityLog.objects.filter(user=request.user, intensity=intensity.upper())
        else:
            logs = ActivityLog.objects.filter(user=request.user)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


class CardioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Cardio activities
    """
    queryset = Cardio.objects.all()
    serializer_class = CardioSerializer
    permission_classes = [IsAuthenticated]


class MusculationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Musculation activities
    """
    queryset = Musculation.objects.all()
    serializer_class = MusculationSerializer
    permission_classes = [IsAuthenticated]


class NatationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Natation activities
    """
    queryset = Natation.objects.all()
    serializer_class = NatationSerializer
    permission_classes = [IsAuthenticated]
