from django.db import models
from apps.users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.db.models import Avg


class Defi(models.Model):
    """Challenge/Defi model"""
    defi_id = models.AutoField(primary_key=True)
    defi_name = models.CharField(max_length=200)
    defi_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'defis'
        verbose_name = 'Défi'
        verbose_name_plural = 'Défis'
    
    def __str__(self):
        return self.defi_name


# Note: signal handler for Defi creation is defined after model classes to avoid
# forward-reference issues. It will create status/badge and default objectives.


class DefiObjectif(models.Model):
    """Challenge Objective"""
    defi = models.ForeignKey(Defi, on_delete=models.CASCADE, related_name='objectives')
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    class Meta:
        db_table = 'defi_objectives'
        verbose_name = 'Défi Objectif'
    
    def __str__(self):
        return f"{self.defi.defi_name} - Objective"


class DefiBadge(models.Model):
    """Challenge Badge"""
    defi = models.OneToOneField(Defi, on_delete=models.CASCADE, related_name='badge')
    gold = models.BooleanField(default=False)
    silver = models.BooleanField(default=False)
    bronze = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'defi_badges'
        verbose_name = 'Défi Badge'
    
    def __str__(self):
        badges = []
        if self.gold:
            badges.append("Gold")
        if self.silver:
            badges.append("Silver")
        if self.bronze:
            badges.append("Bronze")
        return f"{self.defi.defi_name}: {', '.join(badges) if badges else 'No badges'}"


class DefiStatus(models.Model):
    """Challenge Status"""
    defi = models.OneToOneField(Defi, on_delete=models.CASCADE, related_name='status')
    completed = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'defi_status'
        verbose_name = 'Défi Status'
        verbose_name_plural = 'Défi Statuses'
    
    def __str__(self):
        if self.completed:
            status = "Completed"
        elif self.in_progress:
            status = "In Progress"
        else:
            status = "Not Started"
        return f"{self.defi.defi_name}: {status}"


class Participation(models.Model):
    """User Participation in Challenge"""
    participation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    defi = models.ForeignKey(Defi, on_delete=models.CASCADE, related_name='participations')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'participations'
    
    def __str__(self):
        return f"{self.user.username} - {self.defi.defi_name}"


class ParticipationProgress(models.Model):
    """Participation Progress"""
    participation = models.OneToOneField(Participation, on_delete=models.CASCADE, related_name='progress')
    progress_value = models.IntegerField(help_text="Progress percentage (0-100)")
    
    class Meta:
        db_table = 'participation_progress'
        verbose_name_plural = 'Participation Progress'
    
    def __str__(self):
        return f"{self.participation.user.username} - {self.participation.defi.defi_name}: {self.progress_value}%"


class ParticipationNumber(models.Model):
    """Participation Number/Count"""
    participation = models.OneToOneField(Participation, on_delete=models.CASCADE, related_name='number')
    participation_count = models.IntegerField()
    
    class Meta:
        db_table = 'participation_numbers'
    
    def __str__(self):
        return f"{self.participation.user.username} - Count: {self.participation_count}"


class ParticipationRange(models.Model):
    """Participation Range"""
    participation = models.OneToOneField(Participation, on_delete=models.CASCADE, related_name='range')
    range_value = models.IntegerField()
    
    class Meta:
        db_table = 'participation_ranges'
    
    def __str__(self):
        return f"{self.participation.user.username} - Range: {self.range_value}"


# -- Signals and helpers that rely on model classes defined above --
def _recalc_defi_status(defi):
    """Recalculate and persist DefiStatus based on participations and progress."""
    status, _ = DefiStatus.objects.get_or_create(defi=defi)
    now = timezone.now()
    # in_progress if any participation without end_date or with end_date in future
    has_active = defi.participations.filter(models.Q(end_date__isnull=True) | models.Q(end_date__gt=now)).exists()
    status.in_progress = bool(has_active)
    # Determine completion according to configured rule
    # Rules: 'any' (default) = any participant reached threshold,
    # 'all' = all active participants reached threshold,
    # 'average' = average progress >= threshold
    rule = getattr(settings, 'DEFIS_COMPLETED_RULE', 'any')
    threshold = int(getattr(settings, 'DEFIS_COMPLETED_PERCENTAGE', 100))

    if rule == 'all':
        active = defi.participations.filter(models.Q(end_date__isnull=True) | models.Q(end_date__gt=now))
        if not active.exists():
            completed = False
        else:
            # all active must have a progress >= threshold
            completed = True
            for p in active:
                try:
                    val = p.progress.progress_value
                except ParticipationProgress.DoesNotExist:
                    val = 0
                if val < threshold:
                    completed = False
                    break
    elif rule == 'average':
        avg = ParticipationProgress.objects.filter(participation__defi=defi).aggregate(avg=Avg('progress_value'))['avg'] or 0
        completed = (avg >= threshold)
    else:  # default 'any'
        completed = ParticipationProgress.objects.filter(participation__defi=defi, progress_value__gte=threshold).exists()

    status.completed = bool(completed)
    status.save()


@receiver(post_save, sender=Participation)
def create_participation_related(sender, instance, created, **kwargs):
    """When a Participation is created, ensure related helper records exist and update Defi status."""
    if created:
        # initial progress
        ParticipationProgress.objects.get_or_create(participation=instance, defaults={'progress_value': 0})
        # initial number and range defaults
        ParticipationNumber.objects.get_or_create(participation=instance, defaults={'participation_count': 0})
        ParticipationRange.objects.get_or_create(participation=instance, defaults={'range_value': 0})
    # any save (create or update) should trigger a status recalculation for the Defi
    _recalc_defi_status(instance.defi)


@receiver(post_save, sender=ParticipationProgress)
def handle_progress_update(sender, instance, created, **kwargs):
    """When progress updates, possibly award badges and update Defi status."""
    # award badges according to thresholds (simple heuristic)
    defi = instance.participation.defi
    badge, _ = DefiBadge.objects.get_or_create(defi=defi)
    v = instance.progress_value or 0

    # Badge thresholds are configurable via settings.DEFIS_BADGE_THRESHOLDS
    defaults = {'bronze': 50, 'silver': 75, 'gold': 100}
    thresholds = getattr(settings, 'DEFIS_BADGE_THRESHOLDS', defaults)
    # Ensure keys exist
    b_thr = int(thresholds.get('bronze', defaults['bronze']))
    s_thr = int(thresholds.get('silver', defaults['silver']))
    g_thr = int(thresholds.get('gold', defaults['gold']))

    changed = False
    if v >= g_thr and not badge.gold:
        badge.gold = True
        changed = True
    if v >= s_thr and not badge.silver:
        badge.silver = True
        changed = True
    if v >= b_thr and not badge.bronze:
        badge.bronze = True
        changed = True

    if changed:
        badge.save()

    # Recalculate status (completed if any participant reached 100)
    _recalc_defi_status(defi)


@receiver(post_save, sender=Defi)
def create_defi_related(sender, instance, created, **kwargs):
    """When a Defi is created, ensure it has a status, badge and default objectives."""
    if created:
        # Create default status if not exists
        DefiStatus.objects.get_or_create(defi=instance, defaults={'completed': False, 'in_progress': False})
        # Create default badge if not exists
        DefiBadge.objects.get_or_create(defi=instance, defaults={'gold': False, 'silver': False, 'bronze': False})

        # Create default objectives if configured or by default one objective of N days
        default_objs = getattr(settings, 'DEFIS_DEFAULT_OBJECTIVES', None)
        if default_objs and isinstance(default_objs, list):
            for obj in default_objs:
                desc = obj.get('description', f'Default objective for {instance.defi_name}')
                sd = obj.get('start_date')
                ed = obj.get('end_date')
                # If start/end not provided, use now + offsets
                if not sd:
                    sd = timezone.now()
                if not ed:
                    ed = sd + timedelta(days=int(obj.get('days', 7)))
                DefiObjectif.objects.create(defi=instance, description=desc, start_date=sd, end_date=ed)
        else:
            days = int(getattr(settings, 'DEFIS_DEFAULT_OBJECTIVE_DAYS', 7))
            sd = timezone.now()
            ed = sd + timedelta(days=days)
            DefiObjectif.objects.create(defi=instance, description=f'Objectif initial ({days} jours)', start_date=sd, end_date=ed)
