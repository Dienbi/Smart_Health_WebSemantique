from django.db import models
from apps.users.models import User


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
