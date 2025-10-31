from django.contrib import admin
from .models import User, Student, Teacher


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'email', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('created_at',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'classe')
    search_fields = ('user__username', 'classe')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'matier')
    search_fields = ('user__username', 'matier')
