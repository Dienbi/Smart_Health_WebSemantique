from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Base User model extending Django's AbstractUser"""
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username


class Student(models.Model):
    """Student model - subclass of User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    classe = models.CharField(max_length=100, verbose_name="Class")
    
    class Meta:
        db_table = 'students'
    
    def __str__(self):
        return f"Student: {self.user.username} - {self.classe}"


class Teacher(models.Model):
    """Teacher model - subclass of User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    matier = models.CharField(max_length=100, verbose_name="Subject")
    
    class Meta:
        db_table = 'teachers'
    
    def __str__(self):
        return f"Teacher: {self.user.username} - {self.matier}"
