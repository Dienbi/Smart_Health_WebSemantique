from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import HealthRecord, HealthMetric, StudentHealthRecord, TeacherHealthRecord
from .serializers import (
    HealthRecordSerializer, HealthMetricSerializer,
    StudentHealthRecordSerializer, TeacherHealthRecordSerializer
)
from .rdf_service import HealthRecordRDFService


# Staff Required Mixin
class StaffRequiredMixin(UserPassesTestMixin):
    """Require staff status for admin views"""
    def test_func(self):
        return self.request.user.is_staff


class HealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HealthRecord model
    """
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter records by user if not staff"""
        if self.request.user.is_staff:
            return HealthRecord.objects.all()
        return HealthRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request when creating record"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_records(self, request):
        """Get records for current user"""
        records = HealthRecord.objects.filter(user=request.user)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def metric(self, request, pk=None):
        """Get the metric for a specific health record"""
        record = self.get_object()
        if record.health_metric:
            serializer = HealthMetricSerializer(record.health_metric)
            return Response(serializer.data)
        return Response(
            {'message': 'No metric found for this health record'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest health record for current user"""
        record = HealthRecord.objects.filter(user=request.user).first()
        if record:
            serializer = self.get_serializer(record)
            return Response(serializer.data)
        return Response(
            {'message': 'No health records found'},
            status=status.HTTP_404_NOT_FOUND
        )


class HealthMetricViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HealthMetric model
    """
    queryset = HealthMetric.objects.all()
    serializer_class = HealthMetricSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter metrics by user's health records if not staff"""
        if self.request.user.is_staff:
            return HealthMetric.objects.all()
        return HealthMetric.objects.filter(health_records__user=self.request.user).distinct()
    
    @action(detail=False, methods=['get'])
    def my_metrics(self, request):
        """Get metrics for current user"""
        metrics = HealthMetric.objects.filter(health_records__user=request.user).distinct()
        serializer = self.get_serializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get metrics by type"""
        metric_type = request.query_params.get('type', None)
        queryset = self.get_queryset()
        
        if metric_type:
            queryset = queryset.filter(metric_name__icontains=metric_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest_by_type(self, request):
        """Get latest metric of each type for current user"""
        from django.db.models import Max
        
        metric_names = HealthMetric.objects.filter(
            health_records__user=request.user
        ).values_list('metric_name', flat=True).distinct()
        
        latest_metrics = []
        for name in metric_names:
            metric = HealthMetric.objects.filter(
                health_records__user=request.user,
                metric_name=name
            ).order_by('-recorded_at').first()
            if metric:
                latest_metrics.append(metric)
        
        serializer = self.get_serializer(latest_metrics, many=True)
        return Response(serializer.data)


class StudentHealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StudentHealthRecord model
    """
    queryset = StudentHealthRecord.objects.all()
    serializer_class = StudentHealthRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return StudentHealthRecord.objects.all()
        # Students can only see their own records
        return StudentHealthRecord.objects.filter(student__user=self.request.user)


class TeacherHealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TeacherHealthRecord model
    """
    queryset = TeacherHealthRecord.objects.all()
    serializer_class = TeacherHealthRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return TeacherHealthRecord.objects.all()
        # Teachers can only see their own records
        return TeacherHealthRecord.objects.filter(teacher__user=self.request.user)


# Web Interface Views
@login_required
def health_record_list_view(request):
    """Display list of user's health records from Fuseki using SPARQL"""
    rdf_service = HealthRecordRDFService()
    
    try:
        # Get records from Fuseki
        rdf_records = rdf_service.get_health_records_by_user(request.user.id)
        
        # Convert RDF results to Django-like objects for template compatibility
        from datetime import datetime
        records = []
        for rdf_record in rdf_records:
            # Parse dates from RDF (ISO format strings)
            start_date_str = rdf_record.get('startDate', '')
            end_date_str = rdf_record.get('endDate', '')
            created_at_str = rdf_record.get('createdAt', '')
            
            start_date = None
            end_date = None
            created_at = None
            
            if start_date_str:
                try:
                    start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                except:
                    try:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
                    except:
                        pass
            
            if end_date_str:
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                except:
                    try:
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')
                    except:
                        pass
            
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                except:
                    try:
                        created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%S')
                    except:
                        pass
            
            record_obj = type('Record', (), {
                'health_record_id': int(rdf_record.get('recordId', 0)),
                'description': rdf_record.get('description', ''),
                'value': float(rdf_record.get('value')) if rdf_record.get('value') else None,
                'start_date': start_date,
                'end_date': end_date,
                'created_at': created_at,
                'health_metric': type('Metric', (), {
                    'health_metric_id': int(rdf_record.get('metricId')) if rdf_record.get('metricId') else None,
                    'metric_name': rdf_record.get('metricName', ''),
                    'metric_unit': rdf_record.get('metricUnit', '')
                })() if rdf_record.get('metricId') else None
            })()
            records.append(record_obj)
        
        # Get metrics from Django (for dropdown) - can also be from Fuseki
        metrics = HealthMetric.objects.all().order_by('metric_name')
        
        return render(request, 'health_records/record_list.html', {
            'records': records,
            'metrics': metrics
        })
    except Exception as e:
        import traceback
        # Fallback to Django ORM if Fuseki fails
        records = HealthRecord.objects.filter(user=request.user).select_related('health_metric').order_by('-created_at')
        metrics = HealthMetric.objects.all().order_by('metric_name')
        return render(request, 'health_records/record_list.html', {
            'records': records,
            'metrics': metrics,
            'error': f'Fuseki connection failed, using Django ORM: {str(e)}'
        })


@login_required
def health_record_create_view(request):
    """Create a new health record"""
    from django.http import JsonResponse
    if request.method == 'POST':
        from django.utils.dateparse import parse_datetime
        import json
        
        try:
            data = json.loads(request.body)
            
            # Parse dates
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            
            start_date = None
            end_date = None
            
            if start_date_str:
                start_date = parse_datetime(start_date_str)
                if not start_date:
                    # Try parsing as datetime-local format (YYYY-MM-DDTHH:mm)
                    from datetime import datetime
                    try:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
                    except:
                        try:
                            start_date = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M:%S')
                        except:
                            try:
                                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                            except:
                                pass
            
            if end_date_str:
                end_date = parse_datetime(end_date_str)
                if not end_date:
                    # Try parsing as datetime-local format (YYYY-MM-DDTHH:mm)
                    from datetime import datetime
                    try:
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                    except:
                        try:
                            end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M:%S')
                        except:
                            try:
                                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                            except:
                                pass
            
            # Get health_metric if provided
            health_metric = None
            if data.get('health_metric_id'):
                try:
                    health_metric = HealthMetric.objects.get(health_metric_id=data.get('health_metric_id'))
                except HealthMetric.DoesNotExist:
                    pass
            
            # Create health record in Django (signals will sync to Fuseki automatically)
            record = HealthRecord.objects.create(
                user=request.user,
                health_metric=health_metric,
                value=data.get('value') if data.get('value') else None,
                description=data.get('description', ''),
                start_date=start_date,
                end_date=end_date
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Health record created successfully',
                'record_id': record.health_record_id
            })
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc() if request.user.is_staff else None
            }, status=400)
    
    return JsonResponse({'error': 'GET method not allowed'}, status=405)


@login_required
def health_record_update_view(request, record_id):
    """Update a health record"""
    try:
        record = HealthRecord.objects.get(health_record_id=record_id, user=request.user)
    except HealthRecord.DoesNotExist:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Record not found'}, status=404)
    
    if request.method == 'POST':
        from django.http import JsonResponse
        from django.utils.dateparse import parse_datetime
        import json
        
        try:
            data = json.loads(request.body)
            
            # Update fields
            if 'description' in data:
                record.description = data.get('description', '')
            
            if 'value' in data:
                record.value = data.get('value') if data.get('value') else None
            
            # Update health_metric if provided
            if 'health_metric_id' in data:
                if data.get('health_metric_id'):
                    try:
                        record.health_metric = HealthMetric.objects.get(health_metric_id=data.get('health_metric_id'))
                    except HealthMetric.DoesNotExist:
                        record.health_metric = None
                else:
                    record.health_metric = None
            
            # Parse and update dates
            if 'start_date' in data and data.get('start_date'):
                start_date = parse_datetime(data.get('start_date'))
                if not start_date:
                    # Try parsing as datetime-local format (YYYY-MM-DDTHH:mm)
                    from datetime import datetime
                    try:
                        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%dT%H:%M')
                    except:
                        try:
                            start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M:%S')
                        except:
                            try:
                                start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
                            except:
                                pass
                    if start_date:
                        record.start_date = start_date
            else:
                record.start_date = None
            
            if 'end_date' in data:
                if data.get('end_date'):
                    end_date = parse_datetime(data.get('end_date'))
                    if not end_date:
                        # Try parsing as datetime-local format (YYYY-MM-DDTHH:mm)
                        from datetime import datetime
                        try:
                            end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%dT%H:%M')
                        except:
                            try:
                                end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d %H:%M:%S')
                            except:
                                try:
                                    end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')
                                except:
                                    pass
                        if end_date:
                            record.end_date = end_date
                else:
                    record.end_date = None
            
            record.save()  # Signals will sync to Fuseki automatically
            
            return JsonResponse({
                'success': True,
                'message': 'Health record updated successfully',
                'record_id': record.health_record_id
            })
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc() if request.user.is_staff else None
            }, status=400)
    
    return JsonResponse({'error': 'GET method not allowed'}, status=405)


@login_required
def health_record_delete_view(request, record_id):
    """Delete a health record from both Django and Fuseki"""
    try:
        record = HealthRecord.objects.get(health_record_id=record_id, user=request.user)
    except HealthRecord.DoesNotExist:
        from django.http import JsonResponse
        return JsonResponse({'error': 'Record not found'}, status=404)
    
    if request.method == 'POST':
        from django.http import JsonResponse
        record_id_deleted = record.health_record_id
        
        # Delete from Django (signals will delete from Fuseki automatically)
        record.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Health record deleted successfully',
            'record_id': record_id_deleted
        })
    
    from django.http import JsonResponse
    return JsonResponse({'error': 'GET method not allowed'}, status=405)


@login_required
def health_record_detail_view(request, record_id):
    """Get details of a health record from Fuseki using SPARQL"""
    from django.http import JsonResponse
    
    try:
        rdf_service = HealthRecordRDFService()
        rdf_record = rdf_service.get_health_record_by_id(record_id)
        
        if not rdf_record:
            return JsonResponse({'error': 'Record not found'}, status=404)
        
        # Verify user owns this record (check user_id from RDF)
        user_id_from_rdf = rdf_record.get('userId')
        if user_id_from_rdf and str(user_id_from_rdf) != str(request.user.id):
            return JsonResponse({'error': 'Record not found'}, status=404)
        
        # Convert RDF data to JSON response
        data = {
            'health_record_id': int(rdf_record.get('recordId', 0)),
            'description': rdf_record.get('description', ''),
            'value': float(rdf_record.get('value')) if rdf_record.get('value') else None,
            'health_metric_id': int(rdf_record.get('metricId')) if rdf_record.get('metricId') else None,
            'health_metric_name': rdf_record.get('metricName', ''),
            'start_date': rdf_record.get('startDate', ''),
            'end_date': rdf_record.get('endDate', ''),
            'created_at': rdf_record.get('createdAt', ''),
        }
        
        return JsonResponse(data)
    except Exception as e:
        import logging
        logging.error(f"Error getting health record from Fuseki: {str(e)}")
        # Fallback to Django ORM
        try:
            record = HealthRecord.objects.select_related('health_metric').get(health_record_id=record_id, user=request.user)
            data = {
                'health_record_id': record.health_record_id,
                'description': record.description,
                'value': record.value,
                'health_metric_id': record.health_metric.health_metric_id if record.health_metric else None,
                'health_metric_name': record.health_metric.metric_name if record.health_metric else None,
                'start_date': record.start_date.isoformat() if record.start_date else None,
                'end_date': record.end_date.isoformat() if record.end_date else None,
                'created_at': record.created_at.isoformat() if record.created_at else None,
            }
            return JsonResponse(data)
        except HealthRecord.DoesNotExist:
            return JsonResponse({'error': 'Record not found'}, status=404)


# Admin CRUD Views for Health Metrics
class AdminHealthMetricListView(StaffRequiredMixin, generic.ListView):
    model = HealthMetric
    template_name = 'admin/health_records/metric_list.html'
    context_object_name = 'metrics'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = HealthMetric.objects.prefetch_related('health_records', 'health_records__user').order_by('-recorded_at')
        # Optional filtering by health record
        health_record_id = self.request.GET.get('health_record_id')
        if health_record_id:
            queryset = queryset.filter(health_records__health_record_id=health_record_id).distinct()
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all health records for the filter dropdown
        context['health_records'] = HealthRecord.objects.select_related('user', 'health_metric').order_by('-created_at')
        return context


class AdminHealthMetricDetailView(StaffRequiredMixin, generic.DetailView):
    model = HealthMetric
    template_name = 'admin/health_records/metric_detail.html'
    context_object_name = 'metric'
    pk_url_kwarg = 'pk'


class AdminHealthMetricCreateView(StaffRequiredMixin, generic.CreateView):
    model = HealthMetric
    fields = ['metric_name', 'metric_description', 'metric_unit']
    template_name = 'admin/health_records/metric_form.html'
    success_url = reverse_lazy('health_metrics_admin:list')


class AdminHealthMetricUpdateView(StaffRequiredMixin, generic.UpdateView):
    model = HealthMetric
    fields = ['metric_name', 'metric_description', 'metric_unit']
    template_name = 'admin/health_records/metric_form.html'
    success_url = reverse_lazy('health_metrics_admin:list')
    pk_url_kwarg = 'pk'


class AdminHealthMetricDeleteView(StaffRequiredMixin, generic.DeleteView):
    model = HealthMetric
    template_name = 'admin/health_records/metric_confirm_delete.html'
    success_url = reverse_lazy('health_metrics_admin:list')
    pk_url_kwarg = 'pk'
