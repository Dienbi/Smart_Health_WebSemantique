from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime
from .models import Activity, ActivityLog, Cardio, Musculation, Natation, LowIntensityLog, MediumIntensityLog, HighIntensityLog
from .serializers import (
    ActivitySerializer, ActivityLogSerializer,
    CardioSerializer, MusculationSerializer, NatationSerializer
)


class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Activity model
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get all logs for a specific activity"""
        activity = self.get_object()
        logs = activity.logs.all()
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data)


class ActivityLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ActivityLog model
    """
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter logs by user if not staff"""
        if self.request.user.is_staff:
            return ActivityLog.objects.all()
        return ActivityLog.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request when creating log"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_logs(self, request):
        """Get logs for current user"""
        logs = ActivityLog.objects.filter(user=request.user)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_intensity(self, request):
        """Get logs grouped by intensity"""
        intensity = request.query_params.get('intensity', None)
        if intensity:
            logs = ActivityLog.objects.filter(user=request.user, intensity=intensity.upper())
        else:
            logs = ActivityLog.objects.filter(user=request.user)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


class CardioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Cardio activities
    """
    queryset = Cardio.objects.all()
    serializer_class = CardioSerializer
    permission_classes = [IsAuthenticated]


class MusculationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Musculation activities
    """
    queryset = Musculation.objects.all()
    serializer_class = MusculationSerializer
    permission_classes = [IsAuthenticated]


class NatationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Natation activities
    """
    queryset = Natation.objects.all()
    serializer_class = NatationSerializer
    permission_classes = [IsAuthenticated]


# ============== WEB INTERFACE VIEWS FOR USERS (ACTIVITY CRUD) ================

@login_required
def activity_list_view(request):
    """Display list of all activities"""
    activities = Activity.objects.all().order_by('-created_at')
    return render(request, 'activities/activity_list.html', {
        'activities': activities
    })


@login_required
def activity_create_view(request):
    """Create a new activity"""
    if request.method == 'POST':
        # Validate form
        errors = {}
        activity_name = request.POST.get('activity_name', '').strip()
        activity_description = request.POST.get('activity_description', '').strip()
        activity_type = request.POST.get('activity_type', '').strip()
        
        # Validate activity_name
        if not activity_name:
            errors['activity_name'] = "Le nom de l'activité est obligatoire"
        elif len(activity_name) < 3:
            errors['activity_name'] = "Le nom doit contenir au moins 3 caractères"
        elif len(activity_name) > 200:
            errors['activity_name'] = "Le nom ne peut pas dépasser 200 caractères"
        
        # Validate activity_type if provided
        valid_types = ['CARDIO', 'MUSCULATION', 'NATATION', '']
        if activity_type and activity_type not in valid_types:
            errors['activity_type'] = "Type d'activité invalide"
        
        # Validate type-specific fields
        if activity_type == 'CARDIO':
            calories_burned = request.POST.get('calories_burned', '').strip()
            heart_rate = request.POST.get('heart_rate', '').strip()
            if not calories_burned:
                errors['calories_burned'] = "Les calories brûlées sont obligatoires pour le cardio"
            if not heart_rate:
                errors['heart_rate'] = "Le rythme cardiaque est obligatoire pour le cardio"
        elif activity_type == 'MUSCULATION':
            sets = request.POST.get('sets', '').strip()
            repetitions = request.POST.get('repetitions', '').strip()
            weight = request.POST.get('weight', '').strip()
            if not sets:
                errors['sets'] = "Le nombre de séries est obligatoire pour la musculation"
            if not repetitions:
                errors['repetitions'] = "Le nombre de répétitions est obligatoire pour la musculation"
            if not weight:
                errors['weight'] = "Le poids est obligatoire pour la musculation"
        elif activity_type == 'NATATION':
            distance = request.POST.get('distance', '').strip()
            style = request.POST.get('style', '').strip()
            if not distance:
                errors['distance'] = "La distance est obligatoire pour la natation"
            if not style:
                errors['style'] = "Le style est obligatoire pour la natation"
        
        if errors:
            return render(request, 'activities/activity_form.html', {
                'is_create': True,
                'errors': errors,
                'form_data': request.POST
            })
        
        # Create activity
        try:
            activity = Activity.objects.create(
                activity_name=activity_name,
                activity_description=activity_description if activity_description else ''
            )
            
            # Create type-specific activity
            if activity_type == 'CARDIO':
                Cardio.objects.create(
                    activity=activity,
                    calories_burned=float(request.POST.get('calories_burned')),
                    heart_rate=int(request.POST.get('heart_rate'))
                )
            elif activity_type == 'MUSCULATION':
                Musculation.objects.create(
                    activity=activity,
                    sets=int(request.POST.get('sets')),
                    repetitions=int(request.POST.get('repetitions')),
                    weight=int(request.POST.get('weight'))
                )
            elif activity_type == 'NATATION':
                Natation.objects.create(
                    activity=activity,
                    distance=int(request.POST.get('distance')),
                    style=request.POST.get('style')
                )
            
            messages.success(request, "Activité créée avec succès!")
            return redirect('activities:activity-detail', activity_id=activity.activity_id)
        except Exception as e:
            messages.error(request, f"Erreur lors de la création: {str(e)}")
    
    return render(request, 'activities/activity_form.html', {
        'is_create': True
    })


@login_required
def activity_detail_view(request, activity_id):
    """Display details for a specific activity"""
    activity = get_object_or_404(Activity, activity_id=activity_id)
    
    # Get activity type and details
    activity_type = None
    if hasattr(activity, 'cardio_details'):
        activity_type = 'CARDIO'
    elif hasattr(activity, 'musculation_details'):
        activity_type = 'MUSCULATION'
    elif hasattr(activity, 'natation_details'):
        activity_type = 'NATATION'
    
    return render(request, 'activities/activity_detail.html', {
        'activity': activity,
        'activity_type': activity_type
    })


@login_required
def activity_update_view(request, activity_id):
    """Update an activity"""
    activity = get_object_or_404(Activity, activity_id=activity_id)
    
    if request.method == 'POST':
        # Validate form
        errors = {}
        activity_name = request.POST.get('activity_name', '').strip()
        activity_description = request.POST.get('activity_description', '').strip()
        activity_type = request.POST.get('activity_type', '').strip()
        
        # Validate activity_name
        if not activity_name:
            errors['activity_name'] = "Le nom de l'activité est obligatoire"
        elif len(activity_name) < 3:
            errors['activity_name'] = "Le nom doit contenir au moins 3 caractères"
        elif len(activity_name) > 200:
            errors['activity_name'] = "Le nom ne peut pas dépasser 200 caractères"
        
        # Validate activity_type if provided
        valid_types = ['CARDIO', 'MUSCULATION', 'NATATION', '']
        if activity_type and activity_type not in valid_types:
            errors['activity_type'] = "Type d'activité invalide"
        
        # Validate type-specific fields
        if activity_type == 'CARDIO':
            calories_burned = request.POST.get('calories_burned', '').strip()
            heart_rate = request.POST.get('heart_rate', '').strip()
            if not calories_burned:
                errors['calories_burned'] = "Les calories brûlées sont obligatoires pour le cardio"
            if not heart_rate:
                errors['heart_rate'] = "Le rythme cardiaque est obligatoire pour le cardio"
        elif activity_type == 'MUSCULATION':
            sets = request.POST.get('sets', '').strip()
            repetitions = request.POST.get('repetitions', '').strip()
            weight = request.POST.get('weight', '').strip()
            if not sets:
                errors['sets'] = "Le nombre de séries est obligatoire pour la musculation"
            if not repetitions:
                errors['repetitions'] = "Le nombre de répétitions est obligatoire pour la musculation"
            if not weight:
                errors['weight'] = "Le poids est obligatoire pour la musculation"
        elif activity_type == 'NATATION':
            distance = request.POST.get('distance', '').strip()
            style = request.POST.get('style', '').strip()
            if not distance:
                errors['distance'] = "La distance est obligatoire pour la natation"
            if not style:
                errors['style'] = "Le style est obligatoire pour la natation"
        
        if errors:
            return render(request, 'activities/activity_form.html', {
                'is_create': False,
                'activity': activity,
                'errors': errors,
                'form_data': request.POST
            })
        
        # Update activity
        try:
            activity.activity_name = activity_name
            activity.activity_description = activity_description if activity_description else ''
            activity.save()
            
            # Delete existing type-specific activities
            Cardio.objects.filter(activity=activity).delete()
            Musculation.objects.filter(activity=activity).delete()
            Natation.objects.filter(activity=activity).delete()
            
            # Create new type-specific activity
            if activity_type == 'CARDIO':
                Cardio.objects.create(
                    activity=activity,
                    calories_burned=float(request.POST.get('calories_burned')),
                    heart_rate=int(request.POST.get('heart_rate'))
                )
            elif activity_type == 'MUSCULATION':
                Musculation.objects.create(
                    activity=activity,
                    sets=int(request.POST.get('sets')),
                    repetitions=int(request.POST.get('repetitions')),
                    weight=int(request.POST.get('weight'))
                )
            elif activity_type == 'NATATION':
                Natation.objects.create(
                    activity=activity,
                    distance=int(request.POST.get('distance')),
                    style=request.POST.get('style')
                )
            
            messages.success(request, "Activité mise à jour avec succès!")
            return redirect('activities:activity-detail', activity_id=activity.activity_id)
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    
    # Determine current activity type
    current_type = ''
    type_data = {}
    if hasattr(activity, 'cardio_details'):
        current_type = 'CARDIO'
        type_data = {
            'calories_burned': activity.cardio_details.calories_burned,
            'heart_rate': activity.cardio_details.heart_rate
        }
    elif hasattr(activity, 'musculation_details'):
        current_type = 'MUSCULATION'
        type_data = {
            'sets': activity.musculation_details.sets,
            'repetitions': activity.musculation_details.repetitions,
            'weight': activity.musculation_details.weight
        }
    elif hasattr(activity, 'natation_details'):
        current_type = 'NATATION'
        type_data = {
            'distance': activity.natation_details.distance,
            'style': activity.natation_details.style
        }
    
    return render(request, 'activities/activity_form.html', {
        'is_create': False,
        'activity': activity,
        'current_type': current_type,
        'type_data': type_data
    })


@login_required
def activity_delete_view(request, activity_id):
    """Delete an activity"""
    activity = get_object_or_404(Activity, activity_id=activity_id)
    
    if request.method == 'POST':
        activity.delete()
        messages.success(request, "Activité supprimée avec succès!")
        return redirect('activities:activity-list')
    
    return render(request, 'activities/activity_confirm_delete.html', {
        'activity': activity
    })


# ============== WEB INTERFACE VIEWS FOR USERS (ACTIVITY LOG CRUD) ================

@login_required
def activity_log_list_view(request):
    """Display list of user's activity logs"""
    activity_logs = ActivityLog.objects.filter(user=request.user).select_related('activity', 'user').order_by('-date')
    return render(request, 'activities/activity_log_list.html', {
        'activity_logs': activity_logs
    })


@login_required
def activity_log_create_view(request):
    """Create a new activity log"""
    if request.method == 'POST':
        # Validate form
        errors = {}
        activity_id = request.POST.get('activity', '').strip()
        date = request.POST.get('date', '').strip()
        duration = request.POST.get('duration', '').strip()
        intensity = request.POST.get('intensity', '').strip()
        
        # Validate activity
        if not activity_id:
            errors['activity'] = "L'activité est obligatoire"
        else:
            try:
                activity = Activity.objects.get(activity_id=int(activity_id))
            except (Activity.DoesNotExist, ValueError):
                errors['activity'] = "Activité invalide"
        
        # Validate date
        if not date:
            errors['date'] = "La date est obligatoire"
        else:
            try:
                parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                if timezone.is_naive(parsed_date):
                    parsed_date = timezone.make_aware(parsed_date)
                one_year_ago = timezone.now() - timezone.timedelta(days=365)
                one_week_future = timezone.now() + timezone.timedelta(days=7)
                if parsed_date < one_year_ago:
                    errors['date'] = "La date ne peut pas être antérieure à 1 an"
                elif parsed_date > one_week_future:
                    errors['date'] = "La date ne peut pas être postérieure à 1 semaine"
            except (ValueError, TypeError):
                errors['date'] = "Format de date invalide"
        
        # Validate duration
        if not duration:
            errors['duration'] = "La durée est obligatoire"
        else:
            try:
                duration_int = int(duration)
                if duration_int <= 0 or duration_int > 1440:
                    errors['duration'] = "La durée doit être entre 1 et 1440 minutes"
            except ValueError:
                errors['duration'] = "La durée doit être un nombre"
        
        # Validate intensity
        valid_intensities = [choice[0] for choice in ActivityLog.INTENSITY_CHOICES]
        if intensity and intensity not in valid_intensities:
            errors['intensity'] = "Intensité invalide"
        
        if errors:
            activities = Activity.objects.all()
            return render(request, 'activities/activity_log_form.html', {
                'is_create': True,
                'activities': activities,
                'errors': errors,
                'form_data': request.POST
            })
        
        # Create activity log
        try:
            activity = Activity.objects.get(activity_id=int(activity_id))
            activity_log = ActivityLog.objects.create(
                activity=activity,
                user=request.user,
                date=parsed_date,
                duration=int(duration),
                intensity=intensity if intensity else None
            )
            
            # Handle intensity-specific logs
            if intensity == 'LOW':
                breathing_rate = request.POST.get('breathing_rate', '').strip()
                comfort_level = request.POST.get('comfort_level', '').strip()
                if breathing_rate and comfort_level:
                    try:
                        LowIntensityLog.objects.create(
                            activity_log=activity_log,
                            breathing_rate=breathing_rate,
                            comfort_level=int(comfort_level)
                        )
                    except (ValueError, TypeError):
                        pass
            elif intensity == 'MEDIUM':
                active_time = request.POST.get('active_time', '').strip()
                breaks_taken = request.POST.get('breaks_taken', '').strip()
                if active_time and breaks_taken:
                    try:
                        MediumIntensityLog.objects.create(
                            activity_log=activity_log,
                            active_time=int(active_time),
                            breaks_taken=int(breaks_taken)
                        )
                    except (ValueError, TypeError):
                        pass
            elif intensity == 'HIGH':
                lactic_acid_level = request.POST.get('lactic_acid_level', '').strip()
                injury_risk = request.POST.get('injury_risk', '').strip()
                if lactic_acid_level and injury_risk:
                    try:
                        HighIntensityLog.objects.create(
                            activity_log=activity_log,
                            lactic_acid_level=float(lactic_acid_level),
                            injury_risk=injury_risk
                        )
                    except (ValueError, TypeError):
                        pass
            
            messages.success(request, "Journal d'activité créé avec succès!")
            return redirect('activities:activity-log-detail', activity_log_id=activity_log.activity_log_id)
        except Exception as e:
            messages.error(request, f"Erreur lors de la création: {str(e)}")
    
    activities = Activity.objects.all()
    return render(request, 'activities/activity_log_form.html', {
        'is_create': True,
        'activities': activities
    })


@login_required
def activity_log_detail_view(request, activity_log_id):
    """Display details for a specific activity log"""
    activity_log = get_object_or_404(ActivityLog, activity_log_id=activity_log_id, user=request.user)
    return render(request, 'activities/activity_log_detail.html', {
        'activity_log': activity_log
    })


@login_required
def activity_log_update_view(request, activity_log_id):
    """Update an activity log"""
    activity_log = get_object_or_404(ActivityLog, activity_log_id=activity_log_id, user=request.user)
    
    if request.method == 'POST':
        # Validate form
        errors = {}
        activity_id = request.POST.get('activity', '').strip()
        date = request.POST.get('date', '').strip()
        duration = request.POST.get('duration', '').strip()
        intensity = request.POST.get('intensity', '').strip()
        
        # Validate activity
        if not activity_id:
            errors['activity'] = "L'activité est obligatoire"
        else:
            try:
                activity = Activity.objects.get(activity_id=int(activity_id))
            except (Activity.DoesNotExist, ValueError):
                errors['activity'] = "Activité invalide"
        
        # Validate date
        if not date:
            errors['date'] = "La date est obligatoire"
        else:
            try:
                parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                if timezone.is_naive(parsed_date):
                    parsed_date = timezone.make_aware(parsed_date)
            except (ValueError, TypeError):
                errors['date'] = "Format de date invalide"
        
        # Validate duration
        if not duration:
            errors['duration'] = "La durée est obligatoire"
        else:
            try:
                duration_int = int(duration)
                if duration_int <= 0 or duration_int > 1440:
                    errors['duration'] = "La durée doit être entre 1 et 1440 minutes"
            except ValueError:
                errors['duration'] = "La durée doit être un nombre"
        
        if errors:
            activities = Activity.objects.all()
            return render(request, 'activities/activity_log_form.html', {
                'is_create': False,
                'activity_log': activity_log,
                'activities': activities,
                'errors': errors,
                'form_data': request.POST
            })
        
        # Update activity log
        try:
            activity_log.activity = Activity.objects.get(activity_id=int(activity_id))
            activity_log.date = parsed_date
            activity_log.duration = int(duration)
            activity_log.intensity = intensity if intensity else None
            activity_log.save()
            
            # Update intensity-specific logs
            LowIntensityLog.objects.filter(activity_log=activity_log).delete()
            MediumIntensityLog.objects.filter(activity_log=activity_log).delete()
            HighIntensityLog.objects.filter(activity_log=activity_log).delete()
            
            if intensity == 'LOW':
                breathing_rate = request.POST.get('breathing_rate', '').strip()
                comfort_level = request.POST.get('comfort_level', '').strip()
                if breathing_rate and comfort_level:
                    try:
                        LowIntensityLog.objects.create(
                            activity_log=activity_log,
                            breathing_rate=breathing_rate,
                            comfort_level=int(comfort_level)
                        )
                    except (ValueError, TypeError):
                        pass
            elif intensity == 'MEDIUM':
                active_time = request.POST.get('active_time', '').strip()
                breaks_taken = request.POST.get('breaks_taken', '').strip()
                if active_time and breaks_taken:
                    try:
                        MediumIntensityLog.objects.create(
                            activity_log=activity_log,
                            active_time=int(active_time),
                            breaks_taken=int(breaks_taken)
                        )
                    except (ValueError, TypeError):
                        pass
            elif intensity == 'HIGH':
                lactic_acid_level = request.POST.get('lactic_acid_level', '').strip()
                injury_risk = request.POST.get('injury_risk', '').strip()
                if lactic_acid_level and injury_risk:
                    try:
                        HighIntensityLog.objects.create(
                            activity_log=activity_log,
                            lactic_acid_level=float(lactic_acid_level),
                            injury_risk=injury_risk
                        )
                    except (ValueError, TypeError):
                        pass
            
            messages.success(request, "Journal d'activité mis à jour avec succès!")
            return redirect('activities:activity-log-detail', activity_log_id=activity_log.activity_log_id)
        except Exception as e:
            messages.error(request, f"Erreur lors de la mise à jour: {str(e)}")
    
    activities = Activity.objects.all()
    return render(request, 'activities/activity_log_form.html', {
        'is_create': False,
        'activity_log': activity_log,
        'activities': activities
    })


@login_required
def activity_log_delete_view(request, activity_log_id):
    """Delete an activity log"""
    activity_log = get_object_or_404(ActivityLog, activity_log_id=activity_log_id, user=request.user)
    
    if request.method == 'POST':
        activity_log.delete()
        messages.success(request, "Journal d'activité supprimé avec succès!")
        return redirect('activities:activity-log-list')
    
    return render(request, 'activities/activity_log_confirm_delete.html', {
        'activity_log': activity_log
    })


# ============== BACKOFFICE (ADMIN) VIEWS FOR ACTIVITY ================

class AdminActivityListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin list view for Activity"""
    model = Activity
    template_name = 'admin/activities/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = Activity.objects.all()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(activity_name__icontains=search)
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['page_title'] = 'Gestion des Activités'
        return context


class AdminActivityDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Admin detail view for Activity"""
    model = Activity
    template_name = 'admin/activities/activity_detail.html'
    context_object_name = 'activity'
    pk_url_kwarg = 'pk'
    
    def test_func(self):
        return self.request.user.is_staff


class AdminActivityCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Admin create view for Activity"""
    model = Activity
    template_name = 'admin/activities/activity_form.html'
    fields = ['activity_name', 'activity_description']
    success_url = reverse_lazy('activities_admin:list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        activity = form.save()
        activity_type = self.request.POST.get('activity_type', '').strip()
        
        # Create type-specific activity
        if activity_type == 'CARDIO':
            calories_burned = self.request.POST.get('calories_burned', '').strip()
            heart_rate = self.request.POST.get('heart_rate', '').strip()
            if calories_burned and heart_rate:
                Cardio.objects.create(
                    activity=activity,
                    calories_burned=float(calories_burned),
                    heart_rate=int(heart_rate)
                )
        elif activity_type == 'MUSCULATION':
            sets = self.request.POST.get('sets', '').strip()
            repetitions = self.request.POST.get('repetitions', '').strip()
            weight = self.request.POST.get('weight', '').strip()
            if sets and repetitions and weight:
                Musculation.objects.create(
                    activity=activity,
                    sets=int(sets),
                    repetitions=int(repetitions),
                    weight=int(weight)
                )
        elif activity_type == 'NATATION':
            distance = self.request.POST.get('distance', '').strip()
            style = self.request.POST.get('style', '').strip()
            if distance and style:
                Natation.objects.create(
                    activity=activity,
                    distance=int(distance),
                    style=style
                )
        
        messages.success(self.request, "Activité créée avec succès!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        context['page_title'] = 'Créer une Activité'
        return context


class AdminActivityUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Admin update view for Activity"""
    model = Activity
    template_name = 'admin/activities/activity_form.html'
    fields = ['activity_name', 'activity_description']
    pk_url_kwarg = 'pk'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        activity = form.save()
        activity_type = self.request.POST.get('activity_type', '').strip()
        
        # Delete existing type-specific activities
        Cardio.objects.filter(activity=activity).delete()
        Musculation.objects.filter(activity=activity).delete()
        Natation.objects.filter(activity=activity).delete()
        
        # Create new type-specific activity
        if activity_type == 'CARDIO':
            calories_burned = self.request.POST.get('calories_burned', '').strip()
            heart_rate = self.request.POST.get('heart_rate', '').strip()
            if calories_burned and heart_rate:
                Cardio.objects.create(
                    activity=activity,
                    calories_burned=float(calories_burned),
                    heart_rate=int(heart_rate)
                )
        elif activity_type == 'MUSCULATION':
            sets = self.request.POST.get('sets', '').strip()
            repetitions = self.request.POST.get('repetitions', '').strip()
            weight = self.request.POST.get('weight', '').strip()
            if sets and repetitions and weight:
                Musculation.objects.create(
                    activity=activity,
                    sets=int(sets),
                    repetitions=int(repetitions),
                    weight=int(weight)
                )
        elif activity_type == 'NATATION':
            distance = self.request.POST.get('distance', '').strip()
            style = self.request.POST.get('style', '').strip()
            if distance and style:
                Natation.objects.create(
                    activity=activity,
                    distance=int(distance),
                    style=style
                )
        
        messages.success(self.request, "Activité mise à jour avec succès!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('activities_admin:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        context['page_title'] = 'Modifier une Activité'
        
        # Determine current activity type
        activity = self.get_object()
        current_type = ''
        type_data = {}
        if hasattr(activity, 'cardio_details'):
            current_type = 'CARDIO'
            type_data = {
                'calories_burned': activity.cardio_details.calories_burned,
                'heart_rate': activity.cardio_details.heart_rate
            }
        elif hasattr(activity, 'musculation_details'):
            current_type = 'MUSCULATION'
            type_data = {
                'sets': activity.musculation_details.sets,
                'repetitions': activity.musculation_details.repetitions,
                'weight': activity.musculation_details.weight
            }
        elif hasattr(activity, 'natation_details'):
            current_type = 'NATATION'
            type_data = {
                'distance': activity.natation_details.distance,
                'style': activity.natation_details.style
            }
        
        context['current_type'] = current_type
        context['type_data'] = type_data
        return context


class AdminActivityDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Admin delete view for Activity"""
    model = Activity
    template_name = 'admin/activities/activity_confirm_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('activities_admin:list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Activité supprimée avec succès!")
        return super().delete(request, *args, **kwargs)


# ============== BACKOFFICE (ADMIN) VIEWS FOR ACTIVITY LOG ================

class AdminActivityLogListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Admin list view for ActivityLog"""
    model = ActivityLog
    template_name = 'admin/activities/activity_log_list.html'
    context_object_name = 'activity_logs'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = ActivityLog.objects.select_related('activity', 'user').all()
        search = self.request.GET.get('search', '')
        intensity = self.request.GET.get('intensity', '')
        if search:
            queryset = queryset.filter(activity__activity_name__icontains=search)
        if intensity:
            queryset = queryset.filter(intensity=intensity)
        return queryset.order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_intensity'] = self.request.GET.get('intensity', '')
        context['intensity_choices'] = ActivityLog.INTENSITY_CHOICES
        context['page_title'] = 'Gestion des Journaux d\'Activité'
        return context


class AdminActivityLogDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Admin detail view for ActivityLog"""
    model = ActivityLog
    template_name = 'admin/activities/activity_log_detail.html'
    context_object_name = 'activity_log'
    pk_url_kwarg = 'pk'
    
    def test_func(self):
        return self.request.user.is_staff


class AdminActivityLogCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Admin create view for ActivityLog"""
    model = ActivityLog
    template_name = 'admin/activities/activity_log_form.html'
    fields = ['activity', 'user', 'date', 'duration', 'intensity']
    success_url = reverse_lazy('activities_admin:log-list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, "Journal d'activité créé avec succès!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        context['page_title'] = 'Créer un Journal d\'Activité'
        context['activities'] = Activity.objects.all()
        return context


class AdminActivityLogUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Admin update view for ActivityLog"""
    model = ActivityLog
    template_name = 'admin/activities/activity_log_form.html'
    fields = ['activity', 'user', 'date', 'duration', 'intensity']
    pk_url_kwarg = 'pk'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_success_url(self):
        messages.success(self.request, "Journal d'activité mis à jour avec succès!")
        return reverse_lazy('activities_admin:log-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        context['page_title'] = 'Modifier un Journal d\'Activité'
        context['activities'] = Activity.objects.all()
        return context


class AdminActivityLogDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Admin delete view for ActivityLog"""
    model = ActivityLog
    template_name = 'admin/activities/activity_log_confirm_delete.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('activities_admin:log-list')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Journal d'activité supprimé avec succès!")
        return super().delete(request, *args, **kwargs)
