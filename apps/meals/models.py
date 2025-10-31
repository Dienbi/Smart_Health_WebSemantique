from django.db import models
from apps.users.models import User


class Meal(models.Model):
    """Base Meal model"""
    MEAL_TYPE_CHOICES = [
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('DINNER', 'Dinner'),
        ('SNACK', 'Snack'),
    ]
    
    meal_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    meal_name = models.CharField(max_length=200)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    total_calories = models.IntegerField()
    meal_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'meals'
    
    def __str__(self):
        return f"{self.user.username} - {self.meal_name} ({self.meal_type})"


class FoodItem(models.Model):
    """Food Item model"""
    FOOD_TYPE_CHOICES = [
        ('PROTEIN', 'Protein'),
        ('CARBS', 'Carbohydrates'),
        ('FATS', 'Fats'),
        ('VEGETABLES', 'Vegetables'),
        ('FRUITS', 'Fruits'),
    ]
    
    food_item_id = models.AutoField(primary_key=True)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='food_items')
    food_item_name = models.CharField(max_length=200)
    food_item_description = models.TextField()
    food_type = models.CharField(max_length=20, choices=FOOD_TYPE_CHOICES)
    
    class Meta:
        db_table = 'food_items'
    
    def __str__(self):
        return self.food_item_name


class Calories(models.Model):
    """Calories nutrition info"""
    food_item = models.OneToOneField(FoodItem, on_delete=models.CASCADE, related_name='calories')
    calories_value = models.IntegerField()
    
    class Meta:
        db_table = 'calories'
        verbose_name_plural = 'Calories'
    
    def __str__(self):
        return f"{self.food_item.food_item_name}: {self.calories_value} cal"


class Protein(models.Model):
    """Protein nutrition info"""
    food_item = models.OneToOneField(FoodItem, on_delete=models.CASCADE, related_name='protein')
    protein_value = models.IntegerField(help_text="grams")
    
    class Meta:
        db_table = 'protein'
    
    def __str__(self):
        return f"{self.food_item.food_item_name}: {self.protein_value}g protein"


class Carbs(models.Model):
    """Carbohydrates nutrition info"""
    food_item = models.OneToOneField(FoodItem, on_delete=models.CASCADE, related_name='carbs')
    carbs_value = models.IntegerField(help_text="grams")
    
    class Meta:
        db_table = 'carbs'
        verbose_name_plural = 'Carbs'
    
    def __str__(self):
        return f"{self.food_item.food_item_name}: {self.carbs_value}g carbs"


class Fiber(models.Model):
    """Fiber nutrition info"""
    food_item = models.OneToOneField(FoodItem, on_delete=models.CASCADE, related_name='fiber')
    fiber_value = models.IntegerField(help_text="grams")
    
    class Meta:
        db_table = 'fiber'
    
    def __str__(self):
        return f"{self.food_item.food_item_name}: {self.fiber_value}g fiber"


class Sugar(models.Model):
    """Sugar nutrition info"""
    food_item = models.OneToOneField(FoodItem, on_delete=models.CASCADE, related_name='sugar')
    sugar_value = models.IntegerField(help_text="grams")
    
    class Meta:
        db_table = 'sugar'
    
    def __str__(self):
        return f"{self.food_item.food_item_name}: {self.sugar_value}g sugar"


class Breakfast(models.Model):
    """Breakfast meal details"""
    meal = models.OneToOneField(Meal, on_delete=models.CASCADE, related_name='breakfast_details')
    breakfast_score = models.IntegerField(help_text="Nutritional score (1-100)")
    
    class Meta:
        db_table = 'breakfast_meals'
    
    def __str__(self):
        return f"Breakfast: {self.meal.meal_name} (Score: {self.breakfast_score})"


class Lunch(models.Model):
    """Lunch meal details"""
    meal = models.OneToOneField(Meal, on_delete=models.CASCADE, related_name='lunch_details')
    lunch_score = models.IntegerField(help_text="Nutritional score (1-100)")
    
    class Meta:
        db_table = 'lunch_meals'
        verbose_name_plural = 'Lunches'
    
    def __str__(self):
        return f"Lunch: {self.meal.meal_name} (Score: {self.lunch_score})"


class Dinner(models.Model):
    """Dinner meal details"""
    meal = models.OneToOneField(Meal, on_delete=models.CASCADE, related_name='dinner_details')
    dinner_score = models.IntegerField(help_text="Nutritional score (1-100)")
    
    class Meta:
        db_table = 'dinner_meals'
    
    def __str__(self):
        return f"Dinner: {self.meal.meal_name} (Score: {self.dinner_score})"


class Snack(models.Model):
    """Snack meal details"""
    meal = models.OneToOneField(Meal, on_delete=models.CASCADE, related_name='snack_details')
    snack_score = models.IntegerField(help_text="Nutritional score (1-100)")
    
    class Meta:
        db_table = 'snack_meals'
    
    def __str__(self):
        return f"Snack: {self.meal.meal_name} (Score: {self.snack_score})"
