from rest_framework import serializers
from .models import (
    Habit, HabitLog, HabitLogFrequency, HabitLogNotes,
    Reading, Cooking, Drawing, Journaling
)


class HabitSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('habit_id',)


class HabitLogFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLogFrequency
        fields = '__all__'


class HabitLogNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLogNotes
        fields = '__all__'


class HabitLogSerializer(serializers.ModelSerializer):
    habit = HabitSerializer(read_only=True)
    habit_id = serializers.IntegerField(write_only=True)
    frequency = HabitLogFrequencySerializer(read_only=True)
    notes = HabitLogNotesSerializer(read_only=True)
    
    class Meta:
        model = HabitLog
        fields = '__all__'
        read_only_fields = ('habit_log_id',)


class ReadingSerializer(serializers.ModelSerializer):
    habit = HabitSerializer(read_only=True)
    
    class Meta:
        model = Reading
        fields = '__all__'


class CookingSerializer(serializers.ModelSerializer):
    habit = HabitSerializer(read_only=True)
    
    class Meta:
        model = Cooking
        fields = '__all__'


class DrawingSerializer(serializers.ModelSerializer):
    habit = HabitSerializer(read_only=True)
    
    class Meta:
        model = Drawing
        fields = '__all__'


class JournalingSerializer(serializers.ModelSerializer):
    habit = HabitSerializer(read_only=True)
    
    class Meta:
        model = Journaling
        fields = '__all__'
