from rest_framework import serializers
from .models import User, Student, Teacher


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ('user_id', 'username', 'email', 'created_at', 'updated_at')
        read_only_fields = ('user_id', 'created_at', 'updated_at')


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'


class TeacherSerializer(serializers.ModelSerializer):
    """Serializer for Teacher model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Teacher
        fields = '__all__'
