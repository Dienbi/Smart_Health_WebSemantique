from django.contrib import admin
from .models import (
    Habit, HabitLog, HabitLogFrequency, HabitLogNotes,
    Reading, Cooking, Drawing, Journaling
)


class HabitLogFrequencyInline(admin.StackedInline):
    model = HabitLogFrequency
    extra = 0


class HabitLogNotesInline(admin.StackedInline):
    model = HabitLogNotes
    extra = 0


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('habit_id', 'user', 'habit_name', 'habit_type', 'created_at')
    search_fields = ('user__username', 'habit_name')
    list_filter = ('habit_type', 'created_at')


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ('habit_log_id', 'habit', 'start_date', 'end_date')
    search_fields = ('habit__habit_name', 'habit__user__username')
    list_filter = ('start_date', 'created_at')
    inlines = [HabitLogFrequencyInline, HabitLogNotesInline]
    date_hierarchy = 'start_date'


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('habit', 'book_name', 'pages_read')
    search_fields = ('habit__habit_name', 'book_name')


@admin.register(Cooking)
class CookingAdmin(admin.ModelAdmin):
    list_display = ('habit', 'start_time', 'end_time')
    search_fields = ('habit__habit_name',)


@admin.register(Drawing)
class DrawingAdmin(admin.ModelAdmin):
    list_display = ('habit', 'inspiration')
    search_fields = ('habit__habit_name', 'inspiration', 'description')


@admin.register(Journaling)
class JournalingAdmin(admin.ModelAdmin):
    list_display = ('habit', 'date', 'done')
    search_fields = ('habit__habit_name',)
    list_filter = ('done', 'date')
