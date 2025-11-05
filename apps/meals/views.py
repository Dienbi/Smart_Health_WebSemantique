from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from .models import Meal, FoodItem, Breakfast, Lunch, Dinner, Snack
from .serializers import (
    MealSerializer, FoodItemSerializer,
    BreakfastSerializer, LunchSerializer, DinnerSerializer, SnackSerializer
)


class MealViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Meal model
    """
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter meals by user if not staff"""
        if self.request.user.is_staff:
            return Meal.objects.all()
        return Meal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request when creating meal"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_meals(self, request):
        """Get meals for current user"""
        meals = Meal.objects.filter(user=request.user)
        serializer = self.get_serializer(meals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get meals by type"""
        meal_type = request.query_params.get('type', None)
        if meal_type:
            meals = Meal.objects.filter(user=request.user, meal_type=meal_type.upper())
        else:
            meals = Meal.objects.filter(user=request.user)
        
        serializer = self.get_serializer(meals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's meals for current user"""
        from django.utils import timezone
        today = timezone.now().date()
        meals = Meal.objects.filter(
            user=request.user,
            meal_date__date=today
        )
        serializer = self.get_serializer(meals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def food_items(self, request, pk=None):
        """Get all food items for a specific meal"""
        meal = self.get_object()
        food_items = meal.food_items.all()
        serializer = FoodItemSerializer(food_items, many=True)
        return Response(serializer.data)


class FoodItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FoodItem model
    """
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter food items by user's meals if not staff"""
        if self.request.user.is_staff:
            return FoodItem.objects.all()
        return FoodItem.objects.filter(meal__user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get food items by type"""
        food_type = request.query_params.get('type', None)
        queryset = self.get_queryset()
        
        if food_type:
            queryset = queryset.filter(food_type=food_type.upper())
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BreakfastViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Breakfast meals
    """
    queryset = Breakfast.objects.all()
    serializer_class = BreakfastSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Breakfast.objects.all()
        return Breakfast.objects.filter(meal__user=self.request.user)


class LunchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Lunch meals
    """
    queryset = Lunch.objects.all()
    serializer_class = LunchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Lunch.objects.all()
        return Lunch.objects.filter(meal__user=self.request.user)


class DinnerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Dinner meals
    """
    queryset = Dinner.objects.all()
    serializer_class = DinnerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Dinner.objects.all()
        return Dinner.objects.filter(meal__user=self.request.user)


class SnackViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Snack meals
    """
    queryset = Snack.objects.all()
    serializer_class = SnackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Snack.objects.all()
        return Snack.objects.filter(meal__user=self.request.user)


# ============== WEB INTERFACE VIEWS FOR USERS (MEAL CRUD) ================

from django.contrib import messages
from django.db import transaction

@login_required
def meal_list_view(request):
    """Display list of user's meals"""
    meals = Meal.objects.filter(user=request.user).select_related('user').prefetch_related('food_items').order_by('-meal_date')
    return render(request, 'meals/meal_list.html', {
        'meals': meals
    })


def validate_meal_form(request):
    """Validate meal form data and return errors dictionary"""
    errors = {}
    
    # Validate meal_name
    meal_name = request.POST.get('meal_name', '').strip()
    if not meal_name:
        errors['meal_name'] = "Le nom du repas est obligatoire"
    elif len(meal_name) < 3:
        errors['meal_name'] = "Le nom doit contenir au moins 3 caractères"
    elif len(meal_name) > 200:
        errors['meal_name'] = "Le nom ne peut pas dépasser 200 caractères"
    elif not all(c.isalnum() or c.isspace() or c in ['-', "'", 'À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'à', 'á', 'â', 'ã', 'ä', 'å', 'È', 'É', 'Ê', 'Ë', 'è', 'é', 'ê', 'ë', 'Ì', 'Í', 'Î', 'Ï', 'ì', 'í', 'î', 'ï', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', 'Ø', 'ò', 'ó', 'ô', 'õ', 'ö', 'ø', 'Ù', 'Ú', 'Û', 'Ü', 'ù', 'ú', 'û', 'ü', 'Ý', 'ý', 'ÿ', 'Ñ', 'ñ', 'Ç', 'ç'] for c in meal_name):
        errors['meal_name'] = "Le nom ne peut contenir que des lettres, chiffres, espaces et tirets"
    
    # Validate meal_type
    meal_type = request.POST.get('meal_type', '').strip()
    valid_meal_types = [choice[0] for choice in Meal.MEAL_TYPE_CHOICES]
    if not meal_type:
        errors['meal_type'] = "Le type de repas est obligatoire"
    elif meal_type not in valid_meal_types:
        errors['meal_type'] = "Type de repas invalide. Veuillez sélectionner un type valide"
    
    # Validate meal_date
    meal_date = request.POST.get('meal_date', '').strip()
    if not meal_date:
        errors['meal_date'] = "La date et l'heure du repas sont obligatoires"
    else:
        from django.utils import timezone
        from datetime import datetime
        try:
            # Try to parse the datetime
            parsed_date = datetime.fromisoformat(meal_date.replace('Z', '+00:00'))
            # Convert to timezone-aware datetime
            if timezone.is_naive(parsed_date):
                parsed_date = timezone.make_aware(parsed_date)
            # Check if date is not too far in the past (more than 1 year)
            one_year_ago = timezone.now() - timezone.timedelta(days=365)
            if parsed_date < one_year_ago:
                errors['meal_date'] = "La date ne peut pas être antérieure à 1 an"
            # Check if date is not too far in the future (more than 1 week)
            one_week_future = timezone.now() + timezone.timedelta(days=7)
            if parsed_date > one_week_future:
                errors['meal_date'] = "La date ne peut pas être postérieure à 1 semaine"
        except (ValueError, TypeError):
            errors['meal_date'] = "Format de date invalide. Utilisez le format: JJ/MM/AAAA HH:MM"
    
    return errors, meal_name, meal_type, meal_date


@login_required
def meal_create_view(request):
    """Create a new meal"""
    if request.method == 'POST':
        # Validate form
        errors, meal_name, meal_type, meal_date = validate_meal_form(request)
        
        if errors:
            # Get all food items (available for selection)
            available_food_items = FoodItem.objects.all().prefetch_related('calories', 'protein', 'carbs')
            
            # Get selected food items to maintain selection
            food_items_ids = request.POST.getlist('food_items')
            
            return render(request, 'meals/meal_form.html', {
                'is_create': True,
                'food_items': available_food_items,
                'meal_types': Meal.MEAL_TYPE_CHOICES,
                'errors': errors,
                'form_data': {
                    'meal_name': meal_name,
                    'meal_type': meal_type,
                    'meal_date': meal_date,
                    'selected_food_items': food_items_ids,
                }
            })
        
        try:
            with transaction.atomic():
                # Get form data
                food_items_ids = request.POST.getlist('food_items')
                
                # Calculate total calories from selected food items
                total_calories = 0
                if food_items_ids:
                    selected_items = FoodItem.objects.filter(food_item_id__in=food_items_ids).prefetch_related('calories')
                    for item in selected_items:
                        if hasattr(item, 'calories'):
                            total_calories += item.calories.calories_value
                
                # Parse and prepare date
                from django.utils import timezone
                from datetime import datetime
                parsed_date = datetime.fromisoformat(meal_date.replace('Z', '+00:00'))
                if timezone.is_naive(parsed_date):
                    parsed_date = timezone.make_aware(parsed_date)
                
                # Create meal
                meal = Meal.objects.create(
                    user=request.user,
                    meal_name=meal_name,
                    meal_type=meal_type,
                    total_calories=total_calories,
                    meal_date=parsed_date
                )
                
                # Associate food items with meal
                if food_items_ids:
                    FoodItem.objects.filter(food_item_id__in=food_items_ids).update(meal=meal)
                
                messages.success(request, f'✅ Repas "{meal_name}" créé avec succès !')
                return redirect('meals:meal-detail', pk=meal.meal_id)
                
        except Exception as e:
            messages.error(request, f'❌ Erreur lors de la création du repas : {str(e)}')
    
    # Get all food items (available for selection)
    available_food_items = FoodItem.objects.all().prefetch_related('calories', 'protein', 'carbs')
    
    return render(request, 'meals/meal_form.html', {
        'is_create': True,
        'food_items': available_food_items,
        'meal_types': Meal.MEAL_TYPE_CHOICES,
        'form_data': {},
    })


@login_required
def meal_detail_view(request, pk):
    """Display meal details"""
    meal = get_object_or_404(Meal, meal_id=pk, user=request.user)
    food_items = meal.food_items.all().prefetch_related('calories', 'protein', 'carbs', 'fiber', 'sugar')
    
    return render(request, 'meals/meal_detail.html', {
        'meal': meal,
        'food_items': food_items,
    })


@login_required
def meal_update_view(request, pk):
    """Update a meal"""
    meal = get_object_or_404(Meal, meal_id=pk, user=request.user)
    
    if request.method == 'POST':
        # Validate form
        errors, meal_name, meal_type, meal_date = validate_meal_form(request)
        
        if errors:
            # Get all food items (available for selection)
            available_food_items = FoodItem.objects.all().prefetch_related('calories', 'protein', 'carbs')
            
            # Get selected food items to maintain selection
            food_items_ids = request.POST.getlist('food_items')
            
            return render(request, 'meals/meal_form.html', {
                'is_create': False,
                'meal': meal,
                'food_items': available_food_items,
                'current_food_items_ids': food_items_ids,
                'meal_types': Meal.MEAL_TYPE_CHOICES,
                'errors': errors,
                'form_data': {
                    'meal_name': meal_name,
                    'meal_type': meal_type,
                    'meal_date': meal_date,
                    'selected_food_items': food_items_ids,
                }
            })
        
        try:
            with transaction.atomic():
                # Get form data
                food_items_ids = request.POST.getlist('food_items')
                
                # Remove old food items association
                FoodItem.objects.filter(meal=meal).update(meal=None)
                
                # Calculate total calories from selected food items
                total_calories = 0
                if food_items_ids:
                    selected_items = FoodItem.objects.filter(food_item_id__in=food_items_ids).prefetch_related('calories')
                    for item in selected_items:
                        if hasattr(item, 'calories'):
                            total_calories += item.calories.calories_value
                
                # Parse and prepare date
                from django.utils import timezone
                from datetime import datetime
                parsed_date = datetime.fromisoformat(meal_date.replace('Z', '+00:00'))
                if timezone.is_naive(parsed_date):
                    parsed_date = timezone.make_aware(parsed_date)
                
                # Update meal
                meal.meal_name = meal_name
                meal.meal_type = meal_type
                meal.meal_date = parsed_date
                meal.total_calories = total_calories
                meal.save()
                
                # Associate new food items with meal
                if food_items_ids:
                    FoodItem.objects.filter(food_item_id__in=food_items_ids).update(meal=meal)
                
                messages.success(request, f'✅ Repas "{meal_name}" modifié avec succès !')
                return redirect('meals:meal-detail', pk=meal.meal_id)
                
        except Exception as e:
            messages.error(request, f'❌ Erreur lors de la modification du repas : {str(e)}')
    
    # Get all food items (available for selection)
    available_food_items = FoodItem.objects.all().prefetch_related('calories', 'protein', 'carbs')
    
    # Get current meal's food items IDs
    current_food_items_ids = list(meal.food_items.values_list('food_item_id', flat=True))
    
    return render(request, 'meals/meal_form.html', {
        'is_create': False,
        'meal': meal,
        'food_items': available_food_items,
        'current_food_items_ids': current_food_items_ids,
        'meal_types': Meal.MEAL_TYPE_CHOICES,
        'form_data': {},
    })


@login_required
def meal_delete_view(request, pk):
    """Delete a meal"""
    meal = get_object_or_404(Meal, meal_id=pk, user=request.user)
    
    if request.method == 'POST':
        meal_name = meal.meal_name
        # Dissociate food items before deletion
        FoodItem.objects.filter(meal=meal).update(meal=None)
        meal.delete()
        messages.success(request, f'✅ Repas "{meal_name}" supprimé avec succès !')
        return redirect('meals:meal-list')
    
    return render(request, 'meals/meal_confirm_delete.html', {
        'meal': meal,
    })


# ============== BACKOFFICE (ADMIN) VIEWS FOR FOODITEM ================
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.forms import inlineformset_factory
from .models import Calories, Protein, Carbs, Fiber, Sugar


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require staff access"""
    def test_func(self):
        return self.request.user.is_staff


class AdminFoodItemListView(StaffRequiredMixin, generic.ListView):
    """Admin view to list all food items"""
    model = FoodItem
    template_name = 'admin/meals/fooditem_list.html'
    context_object_name = 'fooditems'
    paginate_by = 20

    def get_queryset(self):
        queryset = FoodItem.objects.select_related('meal', 'meal__user').prefetch_related(
            'calories', 'protein', 'carbs', 'fiber', 'sugar'
        ).order_by('-food_item_id')
        
        # Add search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(food_item_name__icontains=search)
        
        # Filter by food type
        food_type = self.request.GET.get('type', '')
        if food_type:
            queryset = queryset.filter(food_type=food_type)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['food_types'] = FoodItem.FOOD_TYPE_CHOICES
        context['current_search'] = self.request.GET.get('search', '')
        context['current_type'] = self.request.GET.get('type', '')
        return context


class AdminFoodItemDetailView(StaffRequiredMixin, generic.DetailView):
    """Admin view to see food item details"""
    model = FoodItem
    template_name = 'admin/meals/fooditem_detail.html'
    context_object_name = 'fooditem'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        
        # Get nutritional information
        context['calories'] = getattr(obj, 'calories', None)
        context['protein'] = getattr(obj, 'protein', None)
        context['carbs'] = getattr(obj, 'carbs', None)
        context['fiber'] = getattr(obj, 'fiber', None)
        context['sugar'] = getattr(obj, 'sugar', None)
        
        return context


class AdminFoodItemCreateView(StaffRequiredMixin, generic.CreateView):
    """Admin view to create a new food item"""
    model = FoodItem
    fields = ['food_item_name', 'food_item_description', 'food_type']
    template_name = 'admin/meals/fooditem_form.html'
    success_url = reverse_lazy('meals_admin:list')

    def get_form(self, form_class=None):
        """Add Bootstrap classes to form fields"""
        form = super().get_form(form_class)
        form.fields['food_item_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ex: Poulet grillé'})
        form.fields['food_item_description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Description détaillée de l\'aliment...', 'rows': 4})
        form.fields['food_type'].widget.attrs.update({'class': 'form-select'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        
        # Initialize empty nutritional values for create form
        context['calories_value'] = ''
        context['protein_value'] = ''
        context['carbs_value'] = ''
        context['fiber_value'] = ''
        context['sugar_value'] = ''
        
        return context

    def form_valid(self, form):
        # Save FoodItem instance first
        self.object = form.save()
        
        # Handle nutritional information from POST data
        try:
            calories_value = self.request.POST.get('calories_value', '').strip()
            if calories_value:
                Calories.objects.create(
                    food_item=self.object,
                    calories_value=int(calories_value)
                )
        except (ValueError, TypeError):
            pass
        
        try:
            protein_value = self.request.POST.get('protein_value', '').strip()
            if protein_value:
                Protein.objects.create(
                    food_item=self.object,
                    protein_value=int(protein_value)
                )
        except (ValueError, TypeError):
            pass
        
        try:
            carbs_value = self.request.POST.get('carbs_value', '').strip()
            if carbs_value:
                Carbs.objects.create(
                    food_item=self.object,
                    carbs_value=int(carbs_value)
                )
        except (ValueError, TypeError):
            pass
        
        try:
            fiber_value = self.request.POST.get('fiber_value', '').strip()
            if fiber_value:
                Fiber.objects.create(
                    food_item=self.object,
                    fiber_value=int(fiber_value)
                )
        except (ValueError, TypeError):
            pass
        
        try:
            sugar_value = self.request.POST.get('sugar_value', '').strip()
            if sugar_value:
                Sugar.objects.create(
                    food_item=self.object,
                    sugar_value=int(sugar_value)
                )
        except (ValueError, TypeError):
            pass
        
        return redirect(self.get_success_url())


class AdminFoodItemUpdateView(StaffRequiredMixin, generic.UpdateView):
    """Admin view to update a food item"""
    model = FoodItem
    fields = ['food_item_name', 'food_item_description', 'food_type']
    template_name = 'admin/meals/fooditem_form.html'
    success_url = reverse_lazy('meals_admin:list')

    def get_form(self, form_class=None):
        """Add Bootstrap classes to form fields"""
        form = super().get_form(form_class)
        form.fields['food_item_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ex: Poulet grillé'})
        form.fields['food_item_description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Description détaillée de l\'aliment...', 'rows': 4})
        form.fields['food_type'].widget.attrs.update({'class': 'form-select'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        
        # Get existing nutritional values
        obj = self.object
        context['calories_value'] = getattr(obj.calories, 'calories_value', '') if hasattr(obj, 'calories') else ''
        context['protein_value'] = getattr(obj.protein, 'protein_value', '') if hasattr(obj, 'protein') else ''
        context['carbs_value'] = getattr(obj.carbs, 'carbs_value', '') if hasattr(obj, 'carbs') else ''
        context['fiber_value'] = getattr(obj.fiber, 'fiber_value', '') if hasattr(obj, 'fiber') else ''
        context['sugar_value'] = getattr(obj.sugar, 'sugar_value', '') if hasattr(obj, 'sugar') else ''
        
        return context

    def form_valid(self, form):
        # Save FoodItem instance first
        self.object = form.save()
        
        # Update nutritional information from POST data
        try:
            calories_value = self.request.POST.get('calories_value', '').strip()
            if calories_value:
                Calories.objects.update_or_create(
                    food_item=self.object,
                    defaults={'calories_value': int(calories_value)}
                )
        except (ValueError, TypeError):
            pass
        
        try:
            protein_value = self.request.POST.get('protein_value', '').strip()
            if protein_value:
                Protein.objects.update_or_create(
                    food_item=self.object,
                    defaults={'protein_value': int(protein_value)}
                )
        except (ValueError, TypeError):
            pass
        
        try:
            carbs_value = self.request.POST.get('carbs_value', '').strip()
            if carbs_value:
                Carbs.objects.update_or_create(
                    food_item=self.object,
                    defaults={'carbs_value': int(carbs_value)}
                )
        except (ValueError, TypeError):
            pass
        
        try:
            fiber_value = self.request.POST.get('fiber_value', '').strip()
            if fiber_value:
                Fiber.objects.update_or_create(
                    food_item=self.object,
                    defaults={'fiber_value': int(fiber_value)}
                )
        except (ValueError, TypeError):
            pass
        
        try:
            sugar_value = self.request.POST.get('sugar_value', '').strip()
            if sugar_value:
                Sugar.objects.update_or_create(
                    food_item=self.object,
                    defaults={'sugar_value': int(sugar_value)}
                )
        except (ValueError, TypeError):
            pass
        
        return redirect(self.get_success_url())


class AdminFoodItemDeleteView(StaffRequiredMixin, generic.DeleteView):
    """Admin view to delete a food item"""
    model = FoodItem
    template_name = 'admin/meals/fooditem_confirm_delete.html'
    success_url = reverse_lazy('meals_admin:list')
    context_object_name = 'fooditem'