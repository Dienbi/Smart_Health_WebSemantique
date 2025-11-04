from django.contrib import admin
from .models import (
    Activity, ActivityLog, Cardio, Musculation, Natation,
    LowIntensityLog, MediumIntensityLog, HighIntensityLog
)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_id', 'activity_name', 'created_at')
    search_fields = ('activity_name', 'activity_description')
    list_filter = ('created_at',)


class LowIntensityLogInline(admin.StackedInline):
    model = LowIntensityLog
    extra = 0


class MediumIntensityLogInline(admin.StackedInline):
    model = MediumIntensityLog
    extra = 0


class HighIntensityLogInline(admin.StackedInline):
    model = HighIntensityLog
    extra = 0


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('activity_log_id', 'user', 'activity', 'date', 'duration', 'intensity')
    search_fields = ('user__username', 'activity__activity_name')
    list_filter = ('intensity', 'date')
    inlines = [LowIntensityLogInline, MediumIntensityLogInline, HighIntensityLogInline]
    date_hierarchy = 'date'


@admin.register(Cardio)
class CardioAdmin(admin.ModelAdmin):
    list_display = ('activity', 'calories_burned', 'heart_rate')
    search_fields = ('activity__activity_name',)


@admin.register(Musculation)
class MusculationAdmin(admin.ModelAdmin):
    list_display = ('activity', 'sets', 'repetitions', 'weight')
    search_fields = ('activity__activity_name',)


@admin.register(Natation)
class NatationAdmin(admin.ModelAdmin):
    list_display = ('activity', 'distance', 'style')
    search_fields = ('activity__activity_name',)
    list_filter = ('style',)
