from django.db import models
from apps.users.models import User


class Activity(models.Model):
    """Base Activity model"""
    activity_id = models.AutoField(primary_key=True)
    activity_name = models.CharField(max_length=200)
    activity_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activities'
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return self.activity_name


class ActivityLog(models.Model):
    """Activity Log model"""
    INTENSITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]
    
    activity_log_id = models.AutoField(primary_key=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    date = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    intensity = models.CharField(max_length=10, choices=INTENSITY_CHOICES, null=True, blank=True)
    
    class Meta:
        db_table = 'activity_logs'
    
    def __str__(self):
        return f"{self.user.username} - {self.activity.activity_name} - {self.date}"


class Cardio(models.Model):
    """Cardio Activity"""
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, related_name='cardio_details')
    calories_burned = models.FloatField()
    heart_rate = models.IntegerField(help_text="Heart rate in BPM")
    
    class Meta:
        db_table = 'cardio_activities'
    
    def __str__(self):
        return f"Cardio: {self.activity.activity_name}"


class Musculation(models.Model):
    """Musculation Activity"""
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, related_name='musculation_details')
    sets = models.IntegerField()
    repetitions = models.IntegerField()
    weight = models.IntegerField(help_text="Weight in kg")
    
    class Meta:
        db_table = 'musculation_activities'
    
    def __str__(self):
        return f"Musculation: {self.activity.activity_name}"


class Natation(models.Model):
    """Swimming Activity"""
    STYLE_CHOICES = [
        ('FREESTYLE', 'Freestyle'),
        ('BACKSTROKE', 'Backstroke'),
        ('BREASTSTROKE', 'Breaststroke'),
        ('BUTTERFLY', 'Butterfly'),
        ('PAPILLON', 'Papillon'),
    ]
    
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, related_name='natation_details')
    distance = models.IntegerField(help_text="Distance in meters")
    style = models.CharField(max_length=20, choices=STYLE_CHOICES)
    
    class Meta:
        db_table = 'natation_activities'
    
    def __str__(self):
        return f"Natation: {self.activity.activity_name} - {self.style}"


class LowIntensityLog(models.Model):
    """Low Intensity Activity Log"""
    activity_log = models.OneToOneField(ActivityLog, on_delete=models.CASCADE, related_name='low_intensity')
    breathing_rate = models.CharField(max_length=50)
    comfort_level = models.IntegerField(help_text="Comfort level (1-10)")
    
    class Meta:
        db_table = 'low_intensity_logs'


class MediumIntensityLog(models.Model):
    """Medium Intensity Activity Log"""
    activity_log = models.OneToOneField(ActivityLog, on_delete=models.CASCADE, related_name='medium_intensity')
    active_time = models.IntegerField(help_text="Active time in minutes")
    breaks_taken = models.IntegerField()
    
    class Meta:
        db_table = 'medium_intensity_logs'


class HighIntensityLog(models.Model):
    """High Intensity Activity Log"""
    activity_log = models.OneToOneField(ActivityLog, on_delete=models.CASCADE, related_name='high_intensity')
    lactic_acid_level = models.FloatField()
    injury_risk = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'high_intensity_logs'
