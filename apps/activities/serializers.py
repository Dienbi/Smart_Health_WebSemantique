from rest_framework import serializers
from .models import (
    Activity, ActivityLog, Cardio, Musculation, Natation,
    LowIntensityLog, MediumIntensityLog, HighIntensityLog
)


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class CardioSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    
    class Meta:
        model = Cardio
        fields = '__all__'


class MusculationSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    
    class Meta:
        model = Musculation
        fields = '__all__'


class NatationSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    
    class Meta:
        model = Natation
        fields = '__all__'


class LowIntensityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LowIntensityLog
        fields = '__all__'


class MediumIntensityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediumIntensityLog
        fields = '__all__'


class HighIntensityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighIntensityLog
        fields = '__all__'


class ActivityLogSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)
    activity_id = serializers.IntegerField(write_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    low_intensity = LowIntensityLogSerializer(read_only=True)
    medium_intensity = MediumIntensityLogSerializer(read_only=True)
    high_intensity = HighIntensityLogSerializer(read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = '__all__'
        read_only_fields = ('activity_log_id',)
