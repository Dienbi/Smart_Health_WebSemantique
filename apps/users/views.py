from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import User
from rest_framework import viewsets


def home_view(request):
    """Home page view"""
    return render(request, 'home.html')


def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect based on user type
            if user.is_staff:
                return redirect('dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def signup_view(request):
    """Signup view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type', 'student')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'signup.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, f'Welcome to Smart Health, {user.first_name}!')
            return redirect('home')
        
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'signup.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
@user_passes_test(lambda u: u.is_staff)
def dashboard_view(request):
    """Admin dashboard view"""
    from apps.activities.models import ActivityLog
    from apps.meals.models import Meal
    from apps.health_records.models import HealthRecord
    from apps.habits.models import HabitLog
    from apps.defis.models import Participation
    
    # Get statistics
    total_users = User.objects.count()
    total_activities = ActivityLog.objects.count()
    total_meals = Meal.objects.count()
    total_records = HealthRecord.objects.count()
    total_habits = HabitLog.objects.count()
    total_participations = Participation.objects.count()
    
    # Recent users
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Recent activities
    recent_activities = ActivityLog.objects.select_related('user', 'activity').order_by('-date')[:10]
    
    # Recent meals
    recent_meals = Meal.objects.select_related('user').order_by('-meal_date')[:10]
    
    context = {
        'total_users': total_users,
        'total_activities': total_activities,
        'total_meals': total_meals,
        'total_records': total_records,
        'total_habits': total_habits,
        'total_participations': total_participations,
        'recent_users': recent_users,
        'recent_activities': recent_activities,
        'recent_meals': recent_meals,
        'current_date': timezone.now(),
    }
    
    return render(request, 'dashboard.html', context)
