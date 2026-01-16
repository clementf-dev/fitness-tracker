from django import forms
from django.utils import timezone
from .models import (
    WeightEntry, StepsEntry, ActivityEntry, GymSession, CardioEntry, CaloriesEntry,
    Food, DailyCalorieEntry, MealItem, MealTemplate, MealTemplateItem
)


class WeightEntryForm(forms.ModelForm):
    """Formulaire de saisie manuelle du poids"""
    class Meta:
        model = WeightEntry
        fields = ['date', 'weight', 'body_fat_percentage', 
                  'muscle_mass', 'visceral_fat', 'basal_metabolic_rate']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'body_fat_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'muscle_mass': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'visceral_fat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'basal_metabolic_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().strftime('%Y-%m-%d')


class StepsEntryForm(forms.ModelForm):
    """Formulaire de saisie manuelle des pas"""
    class Meta:
        model = StepsEntry
        fields = ['date', 'steps']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            'steps': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().strftime('%Y-%m-%d')


class ActivityEntryForm(forms.ModelForm):
    """Formulaire de saisie manuelle d'activité"""
    class Meta:
        model = ActivityEntry
        fields = ['date', 'source_app', 'activity_type', 'activity_name', 
                  'elapsed_time', 'active_time', 'distance_km']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            'source_app': forms.TextInput(attrs={'class': 'form-control'}),
            'activity_type': forms.TextInput(attrs={'class': 'form-control'}),
            'activity_name': forms.TextInput(attrs={'class': 'form-control'}),
            'distance_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().strftime('%Y-%m-%d')


class GymSessionForm(forms.ModelForm):
    """Formulaire de saisie de séance de salle"""
    class Meta:
        model = GymSession
        fields = ['date', 'session_type', 'notes']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            'session_type': forms.Select(attrs={
                'class': 'form-select',
                'style': 'background-color: #2b2d42; color: #ffffff; border-color: rgba(255, 255, 255, 0.1);'
            }),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().strftime('%Y-%m-%d')


class CardioEntryForm(forms.ModelForm):
    """Formulaire de saisie de cardio"""
    class Meta:
        model = CardioEntry
        fields = ['date', 'treadmill_minutes', 'speed', 'notes']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            'treadmill_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'speed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().strftime('%Y-%m-%d')


class CaloriesEntryForm(forms.ModelForm):
    """Formulaire de saisie de calories"""
    class Meta:
        model = CaloriesEntry
        fields = ['date', 'calories', 'notes']
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('date'):
            self.initial['date'] = timezone.now().strftime('%Y-%m-%d')


class CSVUploadForm(forms.Form):
    """Formulaire d'upload de fichiers CSV"""
    CSV_TYPE_CHOICES = [
        ('weight', 'Poids'),
        ('steps', 'Pas'),
    ]
    
    csv_type = forms.ChoiceField(
        choices=CSV_TYPE_CHOICES,
        label="Type de fichier CSV",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'background-color: #2b2d42; color: #ffffff; border-color: rgba(255, 255, 255, 0.1);'
        })
    )
    csv_file = forms.FileField(
        label="Fichier CSV",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )


class FoodForm(forms.ModelForm):
    """Formulaire pour ajouter/modifier un aliment"""
    class Meta:
        model = Food
        fields = ['name', 'brand', 'serving_size', 'calories', 'protein', 'carbs', 'fat', 'fiber', 'barcode']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'aliment'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marque (optionnel)'}),
            'serving_size': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '100'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'kcal'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'g'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'g'}),
            'fat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'g'}),
            'fiber': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'g'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code-barres (optionnel)'}),
        }


class MealItemForm(forms.ModelForm):
    """Formulaire pour ajouter un aliment à un repas"""
    class Meta:
        model = MealItem
        fields = ['food', 'meal_type', 'quantity']
        widgets = {
            'food': forms.Select(attrs={
                'class': 'form-select',
                'style': 'background-color: #2b2d42; color: #ffffff; border-color: rgba(255, 255, 255, 0.1);'
            }),
            'meal_type': forms.Select(attrs={
                'class': 'form-select',
                'style': 'background-color: #2b2d42; color: #ffffff; border-color: rgba(255, 255, 255, 0.1);'
            }),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'value': '1'}),
        }


class EditMealItemForm(forms.ModelForm):
    """Formulaire pour modifier UNIQUEMENT la quantité d'un élément de repas"""
    class Meta:
        model = MealItem
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
        }


class QuickMealItemForm(forms.Form):
    """Formulaire rapide pour ajouter un aliment à un repas (sans sélecteur meal_type)"""
    food = forms.ModelChoiceField(
        queryset=Food.objects.all(),
        label="Aliment",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'background-color: #2b2d42; color: #ffffff; border-color: rgba(255, 255, 255, 0.1);'
        })
    )
    quantity = forms.DecimalField(
        initial=1,
        min_value=0.01,
        decimal_places=2,
        label="Quantité (portions)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'value': '1'})
    )


class MealTemplateForm(forms.ModelForm):
    """Formulaire pour créer un repas type"""
    class Meta:
        model = MealTemplate
        fields = ['name', 'meal_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du repas type'}),
            'meal_type': forms.Select(attrs={
                'class': 'form-select',
                'style': 'background-color: #2b2d42; color: #ffffff; border-color: rgba(255, 255, 255, 0.1);'
            }),
        }


class MealTemplateItemForm(forms.ModelForm):
    """Formulaire pour ajouter un aliment à un repas type"""
    class Meta:
        model = MealTemplateItem
        fields = ['food', 'quantity']
        widgets = {
            'food': forms.Select(attrs={
                'class': 'form-select',
                'style': 'background-color: #2b2d42; color: #ffffff; border-color: rgba(255, 255, 255, 0.1);'
            }),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'value': '1'}),
        }


class FoodSearchForm(forms.Form):
    """Formulaire de recherche d'aliments en ligne"""
    query = forms.CharField(
        max_length=200,
        label="Rechercher un aliment",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez le nom d\'un aliment...',
            'autocomplete': 'off'
        })
    )

