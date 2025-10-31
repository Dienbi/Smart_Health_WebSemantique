from django.db import models
from apps.users.models import User


class Habit(models.Model):
    """Base Habit model"""
    HABIT_TYPE_CHOICES = [
        ('READING', 'Reading'),
        ('COOKING', 'Cooking'),
        ('DRAWING', 'Drawing'),
        ('JOURNALING', 'Journaling'),
        ('OTHER', 'Other'),
    ]
    
    habit_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    habit_name = models.CharField(max_length=200)
    habit_type = models.CharField(max_length=20, choices=HABIT_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'habits'
    
    def __str__(self):
        return f"{self.user.username} - {self.habit_name}"


class HabitLog(models.Model):
    """Habit Log model"""
    habit_log_id = models.AutoField(primary_key=True)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    reminder_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'habit_logs'
    
    def __str__(self):
        return f"Log for {self.habit.habit_name} - {self.start_date}"


class HabitLogFrequency(models.Model):
    """Habit Log Frequency"""
    habit_log = models.OneToOneField(HabitLog, on_delete=models.CASCADE, related_name='frequency')
    daily = models.BooleanField(default=False)
    weekly = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'habit_log_frequencies'
        verbose_name_plural = 'Habit Log Frequencies'
    
    def __str__(self):
        freq = []
        if self.daily:
            freq.append("Daily")
        if self.weekly:
            freq.append("Weekly")
        return f"{self.habit_log.habit.habit_name}: {', '.join(freq)}"


class HabitLogNotes(models.Model):
    """Habit Log Notes"""
    habit_log = models.OneToOneField(HabitLog, on_delete=models.CASCADE, related_name='notes')
    description = models.TextField()
    
    class Meta:
        db_table = 'habit_log_notes'
        verbose_name_plural = 'Habit Log Notes'
    
    def __str__(self):
        return f"Notes for {self.habit_log.habit.habit_name}"


class Reading(models.Model):
    """Reading Habit"""
    habit = models.OneToOneField(Habit, on_delete=models.CASCADE, related_name='reading_details')
    book_name = models.CharField(max_length=200)
    pages_read = models.IntegerField()
    
    class Meta:
        db_table = 'reading_habits'
    
    def __str__(self):
        return f"Reading: {self.book_name} ({self.pages_read} pages)"


class Cooking(models.Model):
    """Cooking Habit"""
    habit = models.OneToOneField(Habit, on_delete=models.CASCADE, related_name='cooking_details')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    class Meta:
        db_table = 'cooking_habits'
    
    def __str__(self):
        return f"Cooking: {self.habit.habit_name}"


class Drawing(models.Model):
    """Drawing Habit"""
    habit = models.OneToOneField(Habit, on_delete=models.CASCADE, related_name='drawing_details')
    description = models.TextField()
    inspiration = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'drawing_habits'
    
    def __str__(self):
        return f"Drawing: {self.habit.habit_name}"


class Journaling(models.Model):
    """Journaling Habit"""
    habit = models.OneToOneField(Habit, on_delete=models.CASCADE, related_name='journaling_details')
    date = models.DateTimeField()
    done = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'journaling_habits'
    
    def __str__(self):
        status = "Done" if self.done else "Pending"
        return f"Journaling: {self.habit.habit_name} - {status}"
