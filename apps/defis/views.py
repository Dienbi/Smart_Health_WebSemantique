from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Defi, Participation
from .serializers import DefiSerializer, ParticipationSerializer


class DefiViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Defi (Challenge) model
    """
    queryset = Defi.objects.all()
    serializer_class = DefiSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active challenges"""
        defis = Defi.objects.all()
        serializer = self.get_serializer(defis, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a challenge"""
        defi = self.get_object()
        user = request.user
        
        # Check if user already participating
        if Participation.objects.filter(user=user, defi=defi).exists():
            return Response(
                {'message': 'You are already participating in this challenge'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create participation
        participation = Participation.objects.create(
            user=user,
            defi=defi,
            start_date=timezone.now()
        )
        
        serializer = ParticipationSerializer(participation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Get all participants for a challenge"""
        defi = self.get_object()
        participations = defi.participations.all()
        serializer = ParticipationSerializer(participations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get leaderboard for a challenge"""
        defi = self.get_object()
        participations = defi.participations.order_by('-progress__progress_value')
        serializer = ParticipationSerializer(participations, many=True)
        return Response(serializer.data)


class ParticipationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Participation model
    """
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter participations by user if not staff"""
        if self.request.user.is_staff:
            return Participation.objects.all()
        return Participation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request when creating participation"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_participations(self, request):
        """Get participations for current user"""
        participations = Participation.objects.filter(user=request.user)
        serializer = self.get_serializer(participations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active participations for current user"""
        now = timezone.now()
        participations = Participation.objects.filter(
            user=request.user,
            defi__created_at__lte=now
        ).exclude(end_date__lt=now)
        serializer = self.get_serializer(participations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update progress for a participation"""
        participation = self.get_object()
        progress_value = request.data.get('progress_value', 0)
        
        # Create or update progress
        from .models import ParticipationProgress
        progress, created = ParticipationProgress.objects.get_or_create(
            participation=participation,
            defaults={'progress_value': progress_value}
        )
        
        if not created:
            progress.progress_value = progress_value
            progress.save()
        
        serializer = self.get_serializer(participation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a challenge"""
        participation = self.get_object()
        
        if participation.user != request.user:
            return Response(
                {'message': 'You can only leave your own participations'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        participation.end_date = timezone.now()
        participation.save()
        
        return Response({'message': 'Successfully left the challenge'})
