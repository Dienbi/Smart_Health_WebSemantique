from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Habit, HabitLog, Reading, Cooking, Drawing, Journaling
from .serializers import (
    HabitSerializer, HabitLogSerializer,
    ReadingSerializer, CookingSerializer, DrawingSerializer, JournalingSerializer
)


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Habit model
    """
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter habits by user if not staff"""
        if self.request.user.is_staff:
            return Habit.objects.all()
        return Habit.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request when creating habit"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_habits(self, request):
        """Get habits for current user"""
        habits = Habit.objects.filter(user=request.user)
        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get habits by type"""
        habit_type = request.query_params.get('type', None)
        if habit_type:
            habits = Habit.objects.filter(user=request.user, habit_type=habit_type.upper())
        else:
            habits = Habit.objects.filter(user=request.user)
        
        serializer = self.get_serializer(habits, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get all logs for a specific habit"""
        habit = self.get_object()
        logs = habit.logs.all()
        serializer = HabitLogSerializer(logs, many=True)
        return Response(serializer.data)


class HabitLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HabitLog model
    """
    queryset = HabitLog.objects.all()
    serializer_class = HabitLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter logs by user's habits if not staff"""
        if self.request.user.is_staff:
            return HabitLog.objects.all()
        return HabitLog.objects.filter(habit__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_logs(self, request):
        """Get logs for current user's habits"""
        logs = HabitLog.objects.filter(habit__user=request.user)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


class ReadingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Reading habits
    """
    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Reading.objects.all()
        return Reading.objects.filter(habit__user=self.request.user)


class CookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Cooking habits
    """
    queryset = Cooking.objects.all()
    serializer_class = CookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Cooking.objects.all()
        return Cooking.objects.filter(habit__user=self.request.user)


class DrawingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Drawing habits
    """
    queryset = Drawing.objects.all()
    serializer_class = DrawingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Drawing.objects.all()
        return Drawing.objects.filter(habit__user=self.request.user)


class JournalingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Journaling habits
    """
    queryset = Journaling.objects.all()
    serializer_class = JournalingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Journaling.objects.all()
        return Journaling.objects.filter(habit__user=self.request.user)
