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
        read_only_fields = ('habit_id', 'user', 'created_at')


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
    habit_id = serializers.IntegerField(write_only=True, source='habit.habit_id')
    frequency = HabitLogFrequencySerializer(read_only=True)
    notes = HabitLogNotesSerializer(read_only=True)
    
    # Optional writable fields for creating frequency and notes
    daily = serializers.BooleanField(write_only=True, required=False)
    weekly = serializers.BooleanField(write_only=True, required=False)
    notes_text = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = HabitLog
        fields = '__all__'
        read_only_fields = ('habit_log_id',)
    
    def create(self, validated_data):
        # Extract optional fields
        daily = validated_data.pop('daily', False)
        weekly = validated_data.pop('weekly', False)
        notes_text = validated_data.pop('notes_text', None)
        
        # Fix habit reference
        habit_data = validated_data.pop('habit', {})
        habit_id = habit_data.get('habit_id')
        if habit_id:
            validated_data['habit_id'] = habit_id
        
        # Create the habit log
        habit_log = HabitLog.objects.create(**validated_data)
        
        # Create frequency if specified
        if daily or weekly:
            HabitLogFrequency.objects.create(
                habit_log=habit_log,
                daily=daily,
                weekly=weekly
            )
        
        # Create notes if provided
        if notes_text:
            HabitLogNotes.objects.create(
                habit_log=habit_log,
                description=notes_text
            )
        
        return habit_log
    
    def update(self, instance, validated_data):
        # Extract optional fields
        daily = validated_data.pop('daily', None)
        weekly = validated_data.pop('weekly', None)
        notes_text = validated_data.pop('notes_text', None)
        
        # Fix habit reference
        habit_data = validated_data.pop('habit', None)
        if habit_data:
            habit_id = habit_data.get('habit_id')
            if habit_id:
                validated_data['habit_id'] = habit_id
        
        # Update the habit log
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create frequency
        if daily is not None or weekly is not None:
            frequency, created = HabitLogFrequency.objects.get_or_create(habit_log=instance)
            if daily is not None:
                frequency.daily = daily
            if weekly is not None:
                frequency.weekly = weekly
            frequency.save()
        
        # Update or create notes
        if notes_text is not None:
            notes, created = HabitLogNotes.objects.get_or_create(habit_log=instance)
            notes.description = notes_text
            notes.save()
        
        return instance


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
