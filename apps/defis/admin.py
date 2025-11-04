from django.contrib import admin
from .models import (
    Defi, DefiObjectif, DefiBadge, DefiStatus,
    Participation, ParticipationProgress, ParticipationNumber, ParticipationRange
)


class DefiObjectifInline(admin.TabularInline):
    model = DefiObjectif
    extra = 1


class DefiBadgeInline(admin.StackedInline):
    model = DefiBadge
    extra = 0


class DefiStatusInline(admin.StackedInline):
    model = DefiStatus
    extra = 0


@admin.register(Defi)
class DefiAdmin(admin.ModelAdmin):
    list_display = ('defi_id', 'defi_name', 'created_at')
    search_fields = ('defi_name', 'defi_description')
    list_filter = ('created_at',)
    inlines = [DefiObjectifInline, DefiBadgeInline, DefiStatusInline]


class ParticipationProgressInline(admin.StackedInline):
    model = ParticipationProgress
    extra = 0


class ParticipationNumberInline(admin.StackedInline):
    model = ParticipationNumber
    extra = 0


class ParticipationRangeInline(admin.StackedInline):
    model = ParticipationRange
    extra = 0


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('participation_id', 'user', 'defi', 'start_date', 'end_date')
    search_fields = ('user__username', 'defi__defi_name')
    list_filter = ('start_date', 'created_at')
    inlines = [ParticipationProgressInline, ParticipationNumberInline, ParticipationRangeInline]
    date_hierarchy = 'start_date'


@admin.register(DefiObjectif)
class DefiObjectifAdmin(admin.ModelAdmin):
    list_display = ('defi', 'start_date', 'end_date')
    search_fields = ('defi__defi_name', 'description')
    list_filter = ('start_date', 'end_date')
