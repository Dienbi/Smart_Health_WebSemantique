from django.contrib import admin
from .models import (
    HealthRecord, StudentHealthRecord, TeacherHealthRecord,
    HealthMetric, HeartRate, Cholesterol, SugarLevel, Oxygen, Height, Weight
)


# HealthMetricInline removed - HealthMetric no longer has ForeignKey to HealthRecord


class HeartRateInline(admin.StackedInline):
    model = HeartRate
    extra = 0


class CholesterolInline(admin.StackedInline):
    model = Cholesterol
    extra = 0


class SugarLevelInline(admin.StackedInline):
    model = SugarLevel
    extra = 0


class OxygenInline(admin.StackedInline):
    model = Oxygen
    extra = 0


class HeightInline(admin.StackedInline):
    model = Height
    extra = 0


class WeightInline(admin.StackedInline):
    model = Weight
    extra = 0


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('health_record_id', 'user', 'health_metric', 'value', 'start_date', 'end_date')
    search_fields = ('user__username', 'health_metric__metric_name', 'description')
    list_filter = ('start_date', 'created_at', 'health_metric')
    date_hierarchy = 'start_date'
    fields = ('user', 'health_metric', 'value', 'description', 'start_date', 'end_date')


@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = ('health_metric_id', 'metric_name', 'metric_unit', 'recorded_at', 'get_health_records_count')
    search_fields = ('metric_name', 'health_records__user__username', 'health_records__health_record_name')
    list_filter = ('recorded_at', 'metric_name')
    inlines = [HeartRateInline, CholesterolInline, SugarLevelInline, OxygenInline, HeightInline, WeightInline]
    readonly_fields = ('health_metric_id',)
    
    def get_health_records_count(self, obj):
        """Get count of health records using this metric"""
        return obj.health_records.count()
    get_health_records_count.short_description = 'Health Records'


@admin.register(StudentHealthRecord)
class StudentHealthRecordAdmin(admin.ModelAdmin):
    list_display = ('health_record', 'student')
    search_fields = ('student__user__username', 'health_record__health_record_name')


@admin.register(TeacherHealthRecord)
class TeacherHealthRecordAdmin(admin.ModelAdmin):
    list_display = ('health_record', 'teacher')
    search_fields = ('teacher__user__username', 'health_record__health_record_name')
