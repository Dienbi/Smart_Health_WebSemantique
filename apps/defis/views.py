from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Defi, Participation
from .serializers import DefiSerializer, ParticipationSerializer
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.forms import inlineformset_factory


# Frontend class-based views (regular CRUD)


class DefiListView(generic.ListView):
    model = Defi
    template_name = 'defis/defi_list.html'
    context_object_name = 'defis'

    def get_queryset(self):
        # Prefetch related objects to avoid N+1 queries when rendering many defis
        from django.db.models import Count, Prefetch
        qs = Defi.objects.all().prefetch_related(
            'objectives',
            'badge',
            'status',
            Prefetch('participations', queryset=Participation.objects.select_related('progress'))
        ).annotate(
            objectives_count=Count('objectives', distinct=True),
            participants_count=Count('participations', distinct=True)
        )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        # Attach user's participation and progress to each defi instance to make templating simple
        if user.is_authenticated:
            parts = Participation.objects.filter(user=user, defi__in=ctx['defis']).select_related('progress')
            part_map = {p.defi_id: p for p in parts}
            for defi in ctx['defis']:
                p = part_map.get(getattr(defi, 'defi_id', None))
                setattr(defi, 'user_participation', p)
                if p and hasattr(p, 'progress'):
                    setattr(defi, 'user_progress', p.progress.progress_value)
                else:
                    setattr(defi, 'user_progress', None)
        return ctx


class DefiDetailView(generic.DetailView):
    model = Defi
    template_name = 'defis/defi_detail.html'
    context_object_name = 'defi'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            try:
                participation = Participation.objects.get(user=user, defi=self.object)
            except Participation.DoesNotExist:
                participation = None
            ctx['user_participation'] = participation
            if participation and hasattr(participation, 'progress'):
                ctx['user_progress'] = participation.progress.progress_value
            else:
                ctx['user_progress'] = None
        # add related details to context: objectives, status and badges
        # use the related_name 'objectives' when available; otherwise query the model to be safe
        try:
            if hasattr(self.object, 'objectives'):
                ctx['objectives'] = self.object.objectives.all()
            else:
                from .models import DefiObjectif
                ctx['objectives'] = DefiObjectif.objects.filter(defi=self.object)
        except Exception:
            ctx['objectives'] = []
        ctx['defi_status'] = getattr(self.object, 'status', None)
        ctx['defi_badge'] = getattr(self.object, 'badge', None)
        return ctx



# Backoffice (admin) views - full CRUD, staff-only
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class AdminDefiListView(StaffRequiredMixin, generic.ListView):
    model = Defi
    template_name = 'admin/defis/defi_list.html'
    context_object_name = 'defis'


class AdminDefiDetailView(StaffRequiredMixin, generic.DetailView):
    model = Defi
    template_name = 'admin/defis/defi_detail.html'
    context_object_name = 'defi'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.object
        # related objects
        try:
            if hasattr(obj, 'objectives'):
                ctx['objectives'] = obj.objectives.all()
            else:
                from .models import DefiObjectif
                ctx['objectives'] = DefiObjectif.objects.filter(defi=obj)
        except Exception:
            ctx['objectives'] = []
        ctx['defi_status'] = getattr(obj, 'status', None)
        ctx['defi_badge'] = getattr(obj, 'badge', None)
        # add participations summary
        ctx['participants_count'] = obj.participations.count()
        return ctx


class AdminDefiCreateView(StaffRequiredMixin, generic.CreateView):
    model = Defi
    fields = ['defi_name', 'defi_description']
    template_name = 'admin/defis/defi_form.html'
    success_url = reverse_lazy('defis_admin:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        DefiObjectiveFormSet = inlineformset_factory(Defi, DefiObjectif, fields=('description', 'start_date', 'end_date'), extra=1, can_delete=True)
        if self.request.POST:
            ctx['objectives_formset'] = DefiObjectiveFormSet(self.request.POST)
        else:
            ctx['objectives_formset'] = DefiObjectiveFormSet()
        ctx['badge'] = None
        ctx['status'] = None
        return ctx

    def form_valid(self, form):
        # save Defi instance first
        self.object = form.save()
        DefiObjectiveFormSet = inlineformset_factory(Defi, DefiObjectif, fields=('description', 'start_date', 'end_date'), extra=1, can_delete=True)
        formset = DefiObjectiveFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()

        # handle badge/status fields from POST
        badge_vals = {
            'gold': bool(self.request.POST.get('badge_gold')),
            'silver': bool(self.request.POST.get('badge_silver')),
            'bronze': bool(self.request.POST.get('badge_bronze')),
        }
        DefiBadge.objects.update_or_create(defi=self.object, defaults=badge_vals)

        status_vals = {
            'completed': bool(self.request.POST.get('status_completed')),
            'in_progress': bool(self.request.POST.get('status_in_progress')),
        }
        DefiStatus.objects.update_or_create(defi=self.object, defaults=status_vals)

        return redirect(self.get_success_url())


class AdminDefiUpdateView(StaffRequiredMixin, generic.UpdateView):
    model = Defi
    fields = ['defi_name', 'defi_description']
    template_name = 'admin/defis/defi_form.html'
    success_url = reverse_lazy('defis_admin:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        DefiObjectiveFormSet = inlineformset_factory(Defi, DefiObjectif, fields=('description', 'start_date', 'end_date'), extra=1, can_delete=True)
        if self.request.POST:
            ctx['objectives_formset'] = DefiObjectiveFormSet(self.request.POST, instance=self.object)
        else:
            ctx['objectives_formset'] = DefiObjectiveFormSet(instance=self.object)
        ctx['badge'] = getattr(self.object, 'badge', None)
        ctx['status'] = getattr(self.object, 'status', None)
        return ctx

    def form_valid(self, form):
        self.object = form.save()
        DefiObjectiveFormSet = inlineformset_factory(Defi, DefiObjectif, fields=('description', 'start_date', 'end_date'), extra=1, can_delete=True)
        formset = DefiObjectiveFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()

        # update badge/status
        badge_vals = {
            'gold': bool(self.request.POST.get('badge_gold')),
            'silver': bool(self.request.POST.get('badge_silver')),
            'bronze': bool(self.request.POST.get('badge_bronze')),
        }
        DefiBadge.objects.update_or_create(defi=self.object, defaults=badge_vals)

        status_vals = {
            'completed': bool(self.request.POST.get('status_completed')),
            'in_progress': bool(self.request.POST.get('status_in_progress')),
        }
        DefiStatus.objects.update_or_create(defi=self.object, defaults=status_vals)

        return redirect(self.get_success_url())


class AdminDefiDeleteView(StaffRequiredMixin, generic.DeleteView):
    model = Defi
    template_name = 'admin/defis/defi_confirm_delete.html'
    success_url = reverse_lazy('defis_admin:list')


# ===== Additional admin CRUD views for related models =====
from .models import (
    DefiObjectif, DefiBadge, DefiStatus,
    Participation, ParticipationProgress,
    ParticipationNumber, ParticipationRange
)


class AdminModelListView(StaffRequiredMixin, generic.ListView):
    """Generic list view; set `model` and `template_name` when inheriting or instantiating."""
    template_name = 'admin/defis/generic_list.html'
    context_object_name = 'objects'


class AdminModelDetailView(StaffRequiredMixin, generic.DetailView):
    template_name = 'admin/defis/generic_detail.html'
    context_object_name = 'object'


class AdminModelCreateView(StaffRequiredMixin, generic.CreateView):
    template_name = 'admin/defis/generic_form.html'


class AdminModelUpdateView(StaffRequiredMixin, generic.UpdateView):
    template_name = 'admin/defis/generic_form.html'


class AdminModelDeleteView(StaffRequiredMixin, generic.DeleteView):
    template_name = 'admin/defis/generic_confirm_delete.html'


# Concrete admin views for each model
class AdminParticipationListView(AdminModelListView):
    model = Participation


class AdminParticipationDetailView(AdminModelDetailView):
    model = Participation


class AdminParticipationCreateView(AdminModelCreateView):
    model = Participation
    fields = ['user', 'defi', 'start_date', 'end_date']
    success_url = reverse_lazy('defis_admin:list')


class AdminParticipationUpdateView(AdminModelUpdateView):
    model = Participation
    fields = ['user', 'defi', 'start_date', 'end_date']
    success_url = reverse_lazy('defis_admin:list')


class AdminParticipationDeleteView(AdminModelDeleteView):
    model = Participation
    success_url = reverse_lazy('defis_admin:list')


class AdminProgressListView(AdminModelListView):
    model = ParticipationProgress


class AdminProgressDetailView(AdminModelDetailView):
    model = ParticipationProgress


class AdminProgressCreateView(AdminModelCreateView):
    model = ParticipationProgress
    fields = ['participation', 'progress_value']
    success_url = reverse_lazy('defis_admin:list')


class AdminProgressUpdateView(AdminModelUpdateView):
    model = ParticipationProgress
    fields = ['participation', 'progress_value']
    success_url = reverse_lazy('defis_admin:list')


class AdminProgressDeleteView(AdminModelDeleteView):
    model = ParticipationProgress
    success_url = reverse_lazy('defis_admin:list')


class AdminObjectiveListView(AdminModelListView):
    model = DefiObjectif


class AdminObjectiveCreateView(AdminModelCreateView):
    model = DefiObjectif
    fields = ['defi', 'description', 'start_date', 'end_date']
    success_url = reverse_lazy('defis_admin:objectives_list')


class AdminObjectiveUpdateView(AdminModelUpdateView):
    model = DefiObjectif
    fields = ['defi', 'description', 'start_date', 'end_date']
    success_url = reverse_lazy('defis_admin:objectives_list')


class AdminObjectiveDeleteView(AdminModelDeleteView):
    model = DefiObjectif
    success_url = reverse_lazy('defis_admin:objectives_list')


class AdminBadgeListView(AdminModelListView):
    model = DefiBadge


class AdminBadgeCreateView(AdminModelCreateView):
    model = DefiBadge
    fields = ['defi', 'gold', 'silver', 'bronze']
    success_url = reverse_lazy('defis_admin:badges_list')


class AdminBadgeUpdateView(AdminModelUpdateView):
    model = DefiBadge
    fields = ['defi', 'gold', 'silver', 'bronze']
    success_url = reverse_lazy('defis_admin:badges_list')


class AdminBadgeDeleteView(AdminModelDeleteView):
    model = DefiBadge
    success_url = reverse_lazy('defis_admin:badges_list')


class AdminStatusListView(AdminModelListView):
    model = DefiStatus


class AdminStatusCreateView(AdminModelCreateView):
    model = DefiStatus
    fields = ['defi', 'completed', 'in_progress']
    success_url = reverse_lazy('defis_admin:status_list')


class AdminStatusUpdateView(AdminModelUpdateView):
    model = DefiStatus
    fields = ['defi', 'completed', 'in_progress']
    success_url = reverse_lazy('defis_admin:status_list')


class AdminStatusDeleteView(AdminModelDeleteView):
    model = DefiStatus
    success_url = reverse_lazy('defis_admin:status_list')


class AdminNumberListView(AdminModelListView):
    model = ParticipationNumber


class AdminNumberCreateView(AdminModelCreateView):
    model = ParticipationNumber
    fields = ['participation', 'participation_count']
    success_url = reverse_lazy('defis_admin:numbers_list')


class AdminNumberUpdateView(AdminModelUpdateView):
    model = ParticipationNumber
    fields = ['participation', 'participation_count']
    success_url = reverse_lazy('defis_admin:numbers_list')


class AdminNumberDeleteView(AdminModelDeleteView):
    model = ParticipationNumber
    success_url = reverse_lazy('defis_admin:numbers_list')


class AdminRangeListView(AdminModelListView):
    model = ParticipationRange


class AdminRangeCreateView(AdminModelCreateView):
    model = ParticipationRange
    fields = ['participation', 'range_value']
    success_url = reverse_lazy('defis_admin:ranges_list')


class AdminRangeUpdateView(AdminModelUpdateView):
    model = ParticipationRange
    fields = ['participation', 'range_value']
    success_url = reverse_lazy('defis_admin:ranges_list')


class AdminRangeDeleteView(AdminModelDeleteView):
    model = ParticipationRange
    success_url = reverse_lazy('defis_admin:ranges_list')


class DefiViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Defi (Challenge) model
    """
    queryset = Defi.objects.all()
    serializer_class = DefiSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active challenges"""
        defis = Defi.objects.all()
        serializer = self.get_serializer(defis, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a challenge"""
        defi = self.get_object()
        user = request.user
        
        # Check if user already participating
        if Participation.objects.filter(user=user, defi=defi).exists():
            return Response(
                {'message': 'You are already participating in this challenge'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create participation
        participation = Participation.objects.create(
            user=user,
            defi=defi,
            start_date=timezone.now()
        )
        
        serializer = ParticipationSerializer(participation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Get all participants for a challenge"""
        defi = self.get_object()
        participations = defi.participations.all()
        serializer = ParticipationSerializer(participations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get leaderboard for a challenge"""
        defi = self.get_object()
        participations = defi.participations.order_by('-progress__progress_value')
        serializer = ParticipationSerializer(participations, many=True)
        return Response(serializer.data)


class ParticipationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Participation model
    """
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter participations by user if not staff"""
        if self.request.user.is_staff:
            return Participation.objects.all()
        return Participation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request when creating participation"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_participations(self, request):
        """Get participations for current user"""
        participations = Participation.objects.filter(user=request.user)
        serializer = self.get_serializer(participations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active participations for current user"""
        now = timezone.now()
        participations = Participation.objects.filter(
            user=request.user,
            defi__created_at__lte=now
        ).exclude(end_date__lt=now)
        serializer = self.get_serializer(participations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update progress for a participation"""
        participation = self.get_object()
        progress_value = request.data.get('progress_value', 0)
        
        # Create or update progress
        from .models import ParticipationProgress
        progress, created = ParticipationProgress.objects.get_or_create(
            participation=participation,
            defaults={'progress_value': progress_value}
        )
        
        if not created:
            progress.progress_value = progress_value
            progress.save()
        
        serializer = self.get_serializer(participation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a challenge"""
        participation = self.get_object()

        if participation.user != request.user:
            return Response(
                {'message': 'You can only leave your own participations'},
                status=status.HTTP_403_FORBIDDEN
            )

        participation.end_date = timezone.now()
        participation.save()

        return Response({'message': 'Successfully left the challenge'})


# Front views for participation actions (web UI)
class JoinDefiView(LoginRequiredMixin, View):
    def post(self, request, pk):
        defi = get_object_or_404(Defi, pk=pk)
        user = request.user
        if Participation.objects.filter(user=user, defi=defi).exists():
            return redirect('defis:detail', pk=defi.pk)

        participation = Participation.objects.create(
            user=user,
            defi=defi,
            start_date=timezone.now()
        )
        # create initial progress
        ParticipationProgress.objects.get_or_create(participation=participation, defaults={'progress_value': 0})
        return redirect('defis:detail', pk=defi.pk)


class LeaveDefiView(LoginRequiredMixin, View):
    def post(self, request, pk):
        defi = get_object_or_404(Defi, pk=pk)
        user = request.user
        try:
            participation = Participation.objects.get(user=user, defi=defi)
        except Participation.DoesNotExist:
            return redirect('defis:detail', pk=defi.pk)

        participation.end_date = timezone.now()
        participation.save()
        return redirect('defis:detail', pk=defi.pk)


class UpdateProgressView(LoginRequiredMixin, View):
    """Allow a participant to update their own progress for the given defi."""
    def post(self, request, pk):
        defi = get_object_or_404(Defi, pk=pk)
        user = request.user
        try:
            participation = Participation.objects.get(user=user, defi=defi)
        except Participation.DoesNotExist:
            return HttpResponseBadRequest("Not participating")

        # Expect 'progress_value' in POST
        try:
            value = int(request.POST.get('progress_value', '').strip())
        except Exception:
            return HttpResponseBadRequest("Invalid progress value")

        # Clamp between 0 and 100
        value = max(0, min(100, value))

        progress, _ = ParticipationProgress.objects.get_or_create(participation=participation, defaults={'progress_value': value})
        progress.progress_value = value
        progress.save()

        return redirect('defis:detail', pk=defi.pk)
