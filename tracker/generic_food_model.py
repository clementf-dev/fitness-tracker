

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
