from rest_framework import serializers
from .models import (
    HealthRecord, StudentHealthRecord, TeacherHealthRecord,
    HealthMetric, HeartRate, Cholesterol, SugarLevel, Oxygen, Height, Weight
)


class HeartRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeartRate
        fields = '__all__'


class CholesterolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cholesterol
        fields = '__all__'


class SugarLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SugarLevel
        fields = '__all__'


class OxygenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oxygen
        fields = '__all__'


class HeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Height
        fields = '__all__'


class WeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weight
        fields = '__all__'


class HealthMetricSerializer(serializers.ModelSerializer):
    heart_rate = HeartRateSerializer(read_only=True)
    cholesterol = CholesterolSerializer(read_only=True)
    sugar_level = SugarLevelSerializer(read_only=True)
    oxygen = OxygenSerializer(read_only=True)
    height = HeightSerializer(read_only=True)
    weight = WeightSerializer(read_only=True)
    
    class Meta:
        model = HealthMetric
        fields = '__all__'
        read_only_fields = ('health_metric_id',)


class HealthRecordSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    health_metric_detail = HealthMetricSerializer(source='health_metric', read_only=True)
    
    class Meta:
        model = HealthRecord
        fields = '__all__'
        read_only_fields = ('health_record_id',)


class StudentHealthRecordSerializer(serializers.ModelSerializer):
    health_record = HealthRecordSerializer(read_only=True)
    student_username = serializers.CharField(source='student.user.username', read_only=True)
    
    class Meta:
        model = StudentHealthRecord
        fields = '__all__'


class TeacherHealthRecordSerializer(serializers.ModelSerializer):
    health_record = HealthRecordSerializer(read_only=True)
    teacher_username = serializers.CharField(source='teacher.user.username', read_only=True)
    
    class Meta:
        model = TeacherHealthRecord
        fields = '__all__'
