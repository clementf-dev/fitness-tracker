"""
Calories tracking views - dashboard, meals, and calendar.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta, date
import calendar
import json

from tracker.models import (
    WeightEntry, Food, DailyCalorieEntry, MealItem, MealTemplate, MealTemplateItem,
    OpenFoodFactsProduct
)
from tracker.forms import EditMealItemForm
from tracker.food_constants import GENERIC_FOODS


def calories_dashboard(request, date_str=None):
    """Vue principale du suivi des calories par jour"""
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Obtenir ou créer l'entrée journalière
    daily_entry, created = DailyCalorieEntry.objects.get_or_create(date=selected_date)
    
    # Types de repas avec leurs items
    meal_types = [
        ('LUNCH', 'Déjeuner', '🍽️'),
        ('SNACK_AM', 'Collation 1', '🍎'),
        ('DINNER', 'Dîner', '🌙'),
        ('SNACK_PM', 'Collation 2', '🍪'),
    ]
    
    meals_data = []
    for meal_code, meal_name, meal_icon in meal_types:
        items = daily_entry.items.filter(meal_type=meal_code)
        meal_calories = sum(item.total_calories for item in items)
        meal_protein = sum(item.total_protein for item in items)
        meal_carbs = sum(item.total_carbs for item in items)
        meal_fat = sum(item.total_fat for item in items)
        meal_fiber = sum(item.total_fiber for item in items)
        
        meals_data.append({
            'code': meal_code,
            'name': meal_name,
            'icon': meal_icon,
            'items': items,
            'calories': meal_calories,
            'protein': round(meal_protein, 1),
            'carbs': round(meal_carbs, 1),
            'fat': round(meal_fat, 1),
            'fiber': round(meal_fiber, 1),
        })
    
    # Navigation dates
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)
    
    # Tous les aliments pour le formulaire rapide
    all_foods = Food.objects.all()
    
    # Les repas types disponibles
    templates = MealTemplate.objects.all()
    
    # Récupérer le poids le plus récent pour les calculs par kg
    latest_weight_entry = WeightEntry.objects.filter(date__lte=selected_date).order_by('-date').first()
    current_weight = float(latest_weight_entry.weight) if latest_weight_entry and latest_weight_entry.weight > 0 else 75.0
    
    total_protein = round(daily_entry.total_protein, 1)
    total_carbs = round(daily_entry.total_carbs, 1)
    total_fat = round(daily_entry.total_fat, 1)
    total_fiber = round(daily_entry.total_fiber, 1)

    prot_per_kg = round(total_protein / current_weight, 2)
    carbs_per_kg = round(total_carbs / current_weight, 2)
    fat_per_kg = round(total_fat / current_weight, 2)

    context = {
        'selected_date': selected_date,
        'prev_date': prev_date,
        'next_date': next_date,
        'daily_entry': daily_entry,
        'meals_data': meals_data,
        'all_foods': all_foods,
        'templates': templates,
        'total_calories': daily_entry.total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat,
        'total_fiber': total_fiber,
        'current_weight': current_weight,
        'prot_per_kg': prot_per_kg,
        'carbs_per_kg': carbs_per_kg,
        'fat_per_kg': fat_per_kg,
    }
    return render(request, 'tracker/calories_dashboard.html', context)


@require_POST
def add_meal_item(request, date_str, meal_type):
    """Ajouter un aliment à un repas"""
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Date invalide.')
        return redirect('calories_dashboard')
    
    food_id = request.POST.get('food')
    quantity = request.POST.get('quantity', 1)
    
    if not food_id:
        messages.error(request, 'Veuillez sélectionner un aliment.')
        return redirect('calories_dashboard_date', date_str=date_str)
    
    try:
        # Gestion des IDs spéciaux (génériques et OFF)
        if str(food_id).startswith('generic_'):
            idx = int(str(food_id).split('_')[1])
            food_data = GENERIC_FOODS[idx]
            # Créer ou récupérer l'aliment
            food, _ = Food.objects.get_or_create(
                name=food_data['name'],
                defaults={
                    'calories': food_data['calories'],
                    'protein': food_data['protein'],
                    'carbs': food_data['carbs'],
                    'fat': food_data['fat'],
                    'fiber': food_data.get('fiber', 0),
                    'serving_size': food_data['unit_weight'],
                }
            )
        elif str(food_id).startswith('off_'):
            code = str(food_id).split('_')[1]
            try:
                # Récupérer depuis la base locale OFF
                off_prod = OpenFoodFactsProduct.objects.get(code=code)
                # Créer ou mettre à jour l'aliment
                food, _ = Food.objects.update_or_create(
                    barcode=code,
                    defaults={
                        'name': off_prod.product_name[:200],
                        'brand': off_prod.brands[:200],
                        'calories': round(off_prod.energy_kcal_100g or 0),
                        'protein': round(off_prod.proteins_100g or 0, 1),
                        'carbs': round(off_prod.carbohydrates_100g or 0, 1),
                        'fat': round(off_prod.fat_100g or 0, 1),
                        'fiber': round(off_prod.fiber_100g or 0, 1),
                        'serving_size': 100,
                    }
                )
            except OpenFoodFactsProduct.DoesNotExist:
                messages.error(request, 'Produit introuvable.')
                return redirect('calories_dashboard_date', date_str=date_str)
        else:
            food = Food.objects.get(id=food_id)
        
        daily_entry, _ = DailyCalorieEntry.objects.get_or_create(date=selected_date)
        
        MealItem.objects.create(
            daily_entry=daily_entry,
            food=food,
            meal_type=meal_type,
            quantity=quantity
        )
        
        messages.success(request, f'{food.name} ajouté!')
    except Food.DoesNotExist:
        messages.error(request, 'Aliment non trouvé.')
    except Exception as e:
        messages.error(request, f'Erreur: {str(e)}')
    
    return redirect(f"{reverse('calories_dashboard_date', args=[date_str])}#meal-{meal_type}")


@require_POST
def delete_meal_item(request, item_id):
    """Supprimer un élément de repas"""
    item = get_object_or_404(MealItem, id=item_id)
    date_str = item.daily_entry.date.strftime('%Y-%m-%d')
    meal_type = item.meal_type
    item.delete()
    messages.success(request, 'Élément supprimé.')
    return redirect(f"{reverse('calories_dashboard_date', args=[date_str])}#meal-{meal_type}")


def edit_meal_item(request, item_id):
    """Modifier la quantité d'un élément de repas"""
    item = get_object_or_404(MealItem, id=item_id)
    date_str = item.daily_entry.date.strftime('%Y-%m-%d')
    meal_type = item.meal_type

    if request.method == 'POST':
        form = EditMealItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Portion modifiée.')
            return redirect(f"{reverse('calories_dashboard_date', args=[date_str])}#meal-{meal_type}")
    else:
        form = EditMealItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'date_str': date_str,
    }
    return render(request, 'tracker/edit_meal_item.html', context)


@require_POST
def update_meal_item_order(request):
    """Mise à jour de l'ordre des éléments de repas via AJAX"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_meal_type = data.get('new_meal_type')
        new_order = data.get('new_order')
        
        if not item_id or not new_meal_type or new_order is None:
            return JsonResponse({'status': 'error', 'message': 'Données manquantes'}, status=400)
            
        # Mise à jour du type de repas pour l'élément déplacé
        item = MealItem.objects.get(id=item_id)
        item.meal_type = new_meal_type
        item.save()
        
        # Mise à jour de l'ordre pour TOUS les éléments concernés
        for index, id_val in enumerate(new_order):
            MealItem.objects.filter(id=id_val).update(order=index)
            
        # Récupérer l'entrée journalière pour recalculer les totaux
        daily_entry = item.daily_entry
        
        # Recalculer les totaux journaliers
        daily_stats = {
            'calories': daily_entry.total_calories,
            'protein': float(round(daily_entry.total_protein, 1)),
            'carbs': float(round(daily_entry.total_carbs, 1)),
            'fat': float(round(daily_entry.total_fat, 1)),
            'fiber': float(round(daily_entry.total_fiber, 1)),
        }
        
        # Recalculer les totaux par repas
        meal_stats = {}
        for m_code, _ in MealItem.MEAL_TYPES:
            items = daily_entry.get_items_by_meal(m_code)
            meal_stats[m_code] = {
                'calories': sum(i.total_calories for i in items),
                'protein': float(round(sum(float(i.total_protein) for i in items), 1)),
                'carbs': float(round(sum(float(i.total_carbs) for i in items), 1)),
                'fat': float(round(sum(float(i.total_fat) for i in items), 1)),
                'fiber': float(round(sum(float(i.total_fiber) for i in items), 1)),
            }
            
        return JsonResponse({
            'status': 'success',
            'daily_stats': daily_stats,
            'meal_stats': meal_stats
        })
    except MealItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Élément non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def calories_calendar(request):
    """Calendrier mensuel des calories"""
    today = timezone.now().date()
    
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year, month = today.year, today.month
    
    # Navigation
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    # Construire le calendrier
    cal = calendar.monthcalendar(year, month)
    
    # Récupérer les données de calories pour ce mois
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    entries = DailyCalorieEntry.objects.filter(date__range=[start_date, end_date])
    calories_map = {e.date: e.total_calories for e in entries}
    
    # Construire les données du calendrier
    weeks_data = []
    for week in cal:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append(None)
            else:
                d = date(year, month, day)
                cals = calories_map.get(d, 0)
                week_days.append({
                    'day': day,
                    'date': d,
                    'is_today': d == today,
                    'calories': cals,
                    'has_data': cals > 0,
                })
        weeks_data.append(week_days)
    
    context = {
        'year': year,
        'month': month,
        'month_name': date(year, month, 1).strftime('%B %Y'),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'weeks_data': weeks_data,
    }
    return render(request, 'tracker/calories_calendar.html', context)


@require_POST
def save_meal_as_template(request, date_str, meal_type):
    """Sauvegarder le contenu d'un repas comme nouveau modèle"""
    try:
        current_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return redirect('calories_dashboard')

    # Récupérer l'entrée journalière
    try:
        daily_entry = DailyCalorieEntry.objects.get(date=current_date_obj)
    except DailyCalorieEntry.DoesNotExist:
        messages.error(request, "Aucune donnée pour ce repas.")
        return redirect('calories_dashboard_date', date_str=date_str)

    # Récupérer les aliments du repas spécifique
    meal_items = MealItem.objects.filter(daily_entry=daily_entry, meal_type=meal_type)
    
    if not meal_items.exists():
        messages.warning(request, "Ce repas est vide, impossible de créer un modèle.")
        return redirect('calories_dashboard_date', date_str=date_str)

    template_name = request.POST.get('template_name', f"Repas {date_str}")
    
    # Créer le modèle
    template = MealTemplate.objects.create(
        name=template_name,
        meal_type=meal_type
    )

    # Copier les items
    for item in meal_items:
        MealTemplateItem.objects.create(
            template=template,
            food=item.food,
            quantity=item.quantity
        )

    messages.success(request, f'Nouveau repas type "{template_name}" créé avec succès !')
    return redirect('calories_dashboard_date', date_str=date_str)
