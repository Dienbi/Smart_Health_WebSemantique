from django.db import models
from apps.users.models import User, Student, Teacher


class HealthMetric(models.Model):
    """Health Metric model"""
    health_metric_id = models.AutoField(primary_key=True)
    metric_name = models.CharField(max_length=200)
    metric_description = models.TextField()
    metric_unit = models.CharField(max_length=50)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'health_metrics'
    
    def __str__(self):
        return f"{self.metric_name} ({self.metric_unit})"


class HealthRecord(models.Model):
    """Base Health Record model"""
    health_record_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_records')
    health_metric = models.ForeignKey(HealthMetric, on_delete=models.CASCADE, related_name='health_records', null=True, blank=True)
    value = models.FloatField(null=True, blank=True, help_text="Valeur du metric")
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'health_records'
    
    def __str__(self):
        metric_name = self.health_metric.metric_name if self.health_metric else "Health Record"
        return f"{self.user.username} - {metric_name}"


class StudentHealthRecord(models.Model):
    """Student Health Record"""
    health_record = models.OneToOneField(HealthRecord, on_delete=models.CASCADE, related_name='student_record')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='health_records')
    
    class Meta:
        db_table = 'student_health_records'
    
    def __str__(self):
        return f"Student Health Record: {self.student.user.username}"


class TeacherHealthRecord(models.Model):
    """Teacher Health Record"""
    health_record = models.OneToOneField(HealthRecord, on_delete=models.CASCADE, related_name='teacher_record')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='health_records')
    
    class Meta:
        db_table = 'teacher_health_records'
    
    def __str__(self):
        return f"Teacher Health Record: {self.teacher.user.username}"




class HeartRate(models.Model):
    """Heart Rate metric"""
    health_metric = models.OneToOneField(HealthMetric, on_delete=models.CASCADE, related_name='heart_rate')
    heart_rate_value = models.FloatField(help_text="BPM")
    
    class Meta:
        db_table = 'heart_rate_metrics'
    
    def __str__(self):
        return f"Heart Rate: {self.heart_rate_value} BPM"


class Cholesterol(models.Model):
    """Cholesterol metric"""
    health_metric = models.OneToOneField(HealthMetric, on_delete=models.CASCADE, related_name='cholesterol')
    cholesterol_value = models.FloatField(help_text="mg/dL")
    
    class Meta:
        db_table = 'cholesterol_metrics'
    
    def __str__(self):
        return f"Cholesterol: {self.cholesterol_value} mg/dL"


class SugarLevel(models.Model):
    """Sugar Level metric"""
    health_metric = models.OneToOneField(HealthMetric, on_delete=models.CASCADE, related_name='sugar_level')
    sugar_level_value = models.FloatField(help_text="mg/dL")
    
    class Meta:
        db_table = 'sugar_level_metrics'
    
    def __str__(self):
        return f"Sugar Level: {self.sugar_level_value} mg/dL"


class Oxygen(models.Model):
    """Oxygen Saturation metric"""
    health_metric = models.OneToOneField(HealthMetric, on_delete=models.CASCADE, related_name='oxygen')
    oxygen_value = models.FloatField(help_text="SpO2 %")
    
    class Meta:
        db_table = 'oxygen_metrics'
    
    def __str__(self):
        return f"Oxygen: {self.oxygen_value}%"


class Height(models.Model):
    """Height metric"""
    health_metric = models.OneToOneField(HealthMetric, on_delete=models.CASCADE, related_name='height')
    height_value = models.FloatField(help_text="cm")
    
    class Meta:
        db_table = 'height_metrics'
    
    def __str__(self):
        return f"Height: {self.height_value} cm"


class Weight(models.Model):
    """Weight metric"""
    health_metric = models.OneToOneField(HealthMetric, on_delete=models.CASCADE, related_name='weight')
    weight_value = models.FloatField(help_text="kg")
    
    class Meta:
        db_table = 'weight_metrics'
    
    def __str__(self):
        return f"Weight: {self.weight_value} kg"
