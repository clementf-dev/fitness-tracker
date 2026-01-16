from django.db import models
from django.utils import timezone


class WeightEntry(models.Model):
    """Entrée de poids quotidienne"""
    date = models.DateField(unique=True, verbose_name="Date")
    time = models.TimeField(default=timezone.now, verbose_name="Heure")
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Poids (kg)")
    body_fat_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Graisse corporelle (%)")
    muscle_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Muscle (%)")
    muscle_mass = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Masse musculaire (kg)")
    bone_mass = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Masse osseuse (kg)")
    body_water = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Eau corporelle (kg)")
    visceral_fat = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Graisse viscérale")
    basal_metabolic_rate = models.IntegerField(null=True, blank=True, verbose_name="Métabolisme de base (kcal)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entrée de poids"
        verbose_name_plural = "Entrées de poids"
        ordering = ['-date']

    def __str__(self):
        return f"Poids - {self.date}"


class StepsEntry(models.Model):
    """Entrée de pas quotidienne"""
    date = models.DateField(unique=True, verbose_name="Date")
    time = models.TimeField(default=timezone.now, verbose_name="Heure")
    steps = models.IntegerField(verbose_name="Pas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entrée de pas"
        verbose_name_plural = "Entrées de pas"
        ordering = ['-date']

    def __str__(self):
        return f"Pas - {self.date}"


class ActivityEntry(models.Model):
    """Entrée d'activité quotidienne"""
    date = models.DateField(verbose_name="Date")
    time = models.TimeField(default=timezone.now, verbose_name="Heure")
    source_app = models.CharField(max_length=100, verbose_name="Application source")
    activity_type = models.CharField(max_length=100, verbose_name="Type d'activité")
    activity_name = models.CharField(max_length=200, verbose_name="Nom de l'activité")
    elapsed_time = models.IntegerField(null=True, blank=True, verbose_name="Temps écoulé (s)")
    active_time = models.IntegerField(null=True, blank=True, verbose_name="Temps actif (s)")
    distance_km = models.FloatField(null=True, blank=True, verbose_name="Distance (km)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entrée d'activité"
        verbose_name_plural = "Entrées d'activité"
        ordering = ['-date']

    def __str__(self):
        return f"Activité - {self.date}"


class GymSession(models.Model):
    """Séance de salle de sport"""
    SESSION_TYPES = [
        ('PUSH', 'Push'),
        ('PULL', 'Pull'),
        ('UPPER', 'Upper Body'),
        ('LOWER', 'Lower Body'),
        ('CARDIO', 'Cardio'),
    ]
    
    date = models.DateField(verbose_name="Date")
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES, default='PUSH', verbose_name="Type de séance")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Séance de salle"
        verbose_name_plural = "Séances de salle"
        ordering = ['-date']

    def __str__(self):
        return f"Gym {self.get_session_type_display()} - {self.date}"


class CardioEntry(models.Model):
    """Entrée de cardio quotidien"""
    date = models.DateField(unique=True, verbose_name="Date")
    treadmill_minutes = models.IntegerField(default=0, verbose_name="Marche sur tapis (min)")
    bike_minutes = models.IntegerField(default=0, verbose_name="Vélo (min)")
    speed = models.FloatField(default=4.0, verbose_name="Vitesse (km/h)")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entrée de cardio"
        verbose_name_plural = "Entrées de cardio"
        ordering = ['-date']

    def __str__(self):
        return f"Cardio - {self.date}"

    @property
    def total_minutes(self):
        return self.treadmill_minutes + self.bike_minutes


class CaloriesEntry(models.Model):
    """Entrée de calories ingérées"""
    date = models.DateField(unique=True, verbose_name="Date")
    calories = models.IntegerField(verbose_name="Calories")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entrée de calories"
        verbose_name_plural = "Entrées de calories"
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.calories} cal"


class Food(models.Model):
    """Aliment dans la banque de données nutritionnelle"""
    name = models.CharField(max_length=200, verbose_name="Nom")
    brand = models.CharField(max_length=100, blank=True, verbose_name="Marque")
    serving_size = models.IntegerField(default=100, verbose_name="Portion (g)")
    calories = models.IntegerField(verbose_name="Calories")
    protein = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Protéines (g)")
    carbs = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Glucides (g)")
    fat = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Lipides (g)")
    fiber = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name="Fibres (g)")
    is_custom = models.BooleanField(default=True, verbose_name="Personnalisé")
    barcode = models.CharField(max_length=50, blank=True, verbose_name="Code-barres")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Aliment"
        verbose_name_plural = "Aliments"
        ordering = ['name']

    def __str__(self):
        if self.brand:
            return f"{self.name} ({self.brand})"
        return self.name


class DailyCalorieEntry(models.Model):
    """Entrée journalière de suivi des calories"""
    date = models.DateField(unique=True, verbose_name="Date")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Suivi journalier"
        verbose_name_plural = "Suivis journaliers"
        ordering = ['-date']

    def __str__(self):
        return f"Calories - {self.date}"

    @property
    def total_calories(self):
        return sum(item.total_calories for item in self.items.all())

    @property
    def total_protein(self):
        return sum(item.total_protein for item in self.items.all())

    @property
    def total_carbs(self):
        return sum(item.total_carbs for item in self.items.all())

    @property
    def total_fat(self):
        return sum(item.total_fat for item in self.items.all())

    @property
    def total_fiber(self):
        return sum(item.total_fiber for item in self.items.all())

    def get_items_by_meal(self, meal_type):
        return self.items.filter(meal_type=meal_type)


class MealItem(models.Model):
    """Élément d'un repas lié à une entrée journalière"""
    MEAL_TYPES = [
        ('BREAKFAST', 'Petit-déjeuner'),
        ('LUNCH', 'Déjeuner'),
        ('SNACK_AM', 'Collation 1'),
        ('DINNER', 'Dîner'),
        ('SNACK_PM', 'Collation 2'),
    ]

    daily_entry = models.ForeignKey(
        DailyCalorieEntry, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Entrée journalière"
    )
    food = models.ForeignKey(
        Food, 
        on_delete=models.PROTECT, 
        verbose_name="Aliment"
    )
    meal_type = models.CharField(
        max_length=20, 
        choices=MEAL_TYPES, 
        verbose_name="Type de repas"
    )
    quantity = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1,
        verbose_name="Quantité (portions)"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Élément de repas"
        verbose_name_plural = "Éléments de repas"
        ordering = ['meal_type', 'order', 'created_at']

    def __str__(self):
        return f"{self.food.name} x{self.quantity}"

    @property
    def total_calories(self):
        return int(self.food.calories * float(self.quantity))

    @property
    def total_protein(self):
        return float(self.food.protein) * float(self.quantity)

    @property
    def total_carbs(self):
        return float(self.food.carbs) * float(self.quantity)

    @property
    def total_fat(self):
        return float(self.food.fat) * float(self.quantity)

    @property
    def total_fiber(self):
        return float(self.food.fiber) * float(self.quantity)


class MealTemplate(models.Model):
    """Repas type réutilisable"""
    MEAL_TYPES = MealItem.MEAL_TYPES

    name = models.CharField(max_length=100, verbose_name="Nom du repas type")
    meal_type = models.CharField(
        max_length=20, 
        choices=MEAL_TYPES,
        default='LUNCH',
        verbose_name="Type de repas suggéré"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Repas type"
        verbose_name_plural = "Repas types"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_calories(self):
        return sum(item.total_calories for item in self.template_items.all())

    @property
    def total_protein(self):
        return sum(item.total_protein for item in self.template_items.all())

    @property
    def total_carbs(self):
        return sum(item.total_carbs for item in self.template_items.all())

    @property
    def total_fat(self):
        return sum(item.total_fat for item in self.template_items.all())

    @property
    def total_fiber(self):
        return sum(item.total_fiber for item in self.template_items.all())


class MealTemplateItem(models.Model):
    """Élément d'un repas type"""
    template = models.ForeignKey(
        MealTemplate, 
        on_delete=models.CASCADE, 
        related_name='template_items',
        verbose_name="Repas type"
    )
    food = models.ForeignKey(
        Food, 
        on_delete=models.PROTECT, 
        verbose_name="Aliment"
    )
    quantity = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1,
        verbose_name="Quantité (portions)"
    )

    class Meta:
        verbose_name = "Élément de repas type"
        verbose_name_plural = "Éléments de repas type"

    def __str__(self):
        return f"{self.food.name} x{self.quantity}"

    @property
    def total_calories(self):
        return int(self.food.calories * float(self.quantity))

    @property
    def total_protein(self):
        return float(self.food.protein) * float(self.quantity)

    @property
    def total_carbs(self):
        return float(self.food.carbs) * float(self.quantity)

    @property
    def total_fat(self):
        return float(self.food.fat) * float(self.quantity)

    @property
    def total_fiber(self):
        return float(self.food.fiber) * float(self.quantity)


class GenericFood(models.Model):
    """
    Aliments génériques non transformés avec traçabilité CIQUAL.
    Remplace progressivement la liste GENERIC_FOODS dans views.py.
    """
    # Identification
    name = models.CharField(max_length=200, unique=True, verbose_name="Nom")
    category = models.CharField(max_length=100, verbose_name="Catégorie", help_text="Ex: Fruits, Légumes, Viandes, etc.")
    
    # Données nutritionnelles (pour 100g)
    calories = models.DecimalField(max_digits=6, decimal_places=1, verbose_name="Calories (kcal/100g)")
    protein = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Protéines (g/100g)")
    carbs = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Glucides (g/100g)", help_text="Glucides disponibles (convention EU)")
    fat = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Lipides (g/100g)")
    fiber = models.DecimalField(max_digits=5, decimal_places=1, default=0, verbose_name="Fibres (g/100g)")
    
    # Métadonnées
    unit_weight = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Poids unitaire (g)", help_text="Poids moyen d'une unité (ex: 120g pour une banane)")
    
    # Traçabilité CIQUAL
    ciqual_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Code CIQUAL", help_text="Code de l'aliment dans la base CIQUAL")
    ciqual_name = models.CharField(max_length=300, blank=True, null=True, verbose_name="Nom CIQUAL", help_text="Nom exact dans CIQUAL")
    data_source = models.CharField(max_length=100, default='CIQUAL 2020', verbose_name="Source des données")
    last_verified = models.DateField(auto_now=True, verbose_name="Dernière vérification")
    
    # Recherche
    keywords = models.TextField(verbose_name="Mots-clés", help_text="Mots-clés de recherche séparés par des virgules")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Aliment générique"
        verbose_name_plural = "Aliments génériques"
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def get_keywords_list(self):
        """Retourne la liste des mots-clés."""
        return [k.strip() for k in self.keywords.split(',') if k.strip()]


class OpenFoodFactsProduct(models.Model):
    """
    Produits de la base Open Food Facts (locale).
    Permet de rechercher des produits français sans appeler l'API externe.
    """
    # Identification
    code = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="Code-barres")
    product_name = models.CharField(max_length=500, db_index=True, verbose_name="Nom du produit")
    brands = models.CharField(max_length=500, blank=True, db_index=True, verbose_name="Marques")
    
    # Nutriments pour 100g
    energy_kcal_100g = models.FloatField(null=True, blank=True, verbose_name="Énergie (kcal/100g)")
    proteins_100g = models.FloatField(null=True, blank=True, verbose_name="Protéines (g/100g)")
    carbohydrates_100g = models.FloatField(null=True, blank=True, verbose_name="Glucides (g/100g)")
    fat_100g = models.FloatField(null=True, blank=True, verbose_name="Lipides (g/100g)")
    fiber_100g = models.FloatField(null=True, blank=True, verbose_name="Fibres (g/100g)")
    
    # Métadonnées
    countries = models.CharField(max_length=500, blank=True, verbose_name="Pays")
    categories = models.CharField(max_length=1000, blank=True, verbose_name="Catégories")
    last_modified = models.DateTimeField(null=True, blank=True, verbose_name="Dernière modification OFF")
    
    # Timestamps locaux
    imported_at = models.DateTimeField(auto_now_add=True, verbose_name="Importé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    
    class Meta:
        db_table = 'tracker_openfoodfacts_product'
        verbose_name = "Produit Open Food Facts"
        verbose_name_plural = "Produits Open Food Facts"
        ordering = ['product_name']
        indexes = [
            models.Index(fields=['product_name']),
            models.Index(fields=['brands']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        if self.brands:
            return f"{self.product_name} ({self.brands})"
        return self.product_name
