"""
Meal templates views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import datetime

from tracker.models import MealTemplate, MealTemplateItem, DailyCalorieEntry, MealItem
from tracker.forms import MealTemplateForm, MealTemplateItemForm


def meal_templates(request):
    """Liste des repas types"""
    templates = MealTemplate.objects.all()
    
    context = {
        'templates': templates,
    }
    return render(request, 'tracker/meal_templates.html', context)


def add_meal_template(request):
    """Créer un nouveau repas type"""
    if request.method == 'POST':
        form = MealTemplateForm(request.POST)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'Repas type "{template.name}" créé!')
            return redirect('edit_meal_template', template_id=template.id)
    else:
        form = MealTemplateForm()
    
    return render(request, 'tracker/add_meal_template.html', {'form': form})


def edit_meal_template(request, template_id):
    """Modifier un repas type et ses éléments"""
    template = get_object_or_404(MealTemplate, id=template_id)
    
    if request.method == 'POST':
        if 'update_template' in request.POST:
            # Mise à jour des infos du template (Nom, Type de repas)
            template_form = MealTemplateForm(request.POST, instance=template)
            if template_form.is_valid():
                template_form.save()
                messages.success(request, 'Informations mises à jour.')
                return redirect('edit_meal_template', template_id=template_id)
            item_form = MealTemplateItemForm()
        else:
            # Ajouter un nouvel élément
            item_form = MealTemplateItemForm(request.POST)
            template_form = MealTemplateForm(instance=template)
            
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.template = template
                item.save()
                messages.success(request, f'{item.food.name} ajouté au repas type!')
                return redirect('edit_meal_template', template_id=template_id)
    else:
        template_form = MealTemplateForm(instance=template)
        item_form = MealTemplateItemForm()
    
    context = {
        'template': template,
        'template_form': template_form,
        'form': item_form,
        'items': template.template_items.all(),
    }
    return render(request, 'tracker/edit_meal_template.html', context)


@require_POST
def delete_meal_template(request, template_id):
    """Supprimer un repas type"""
    template = get_object_or_404(MealTemplate, id=template_id)
    template_name = template.name
    template.delete()
    messages.success(request, f'Repas type "{template_name}" supprimé.')
    return redirect('meal_templates')


@require_POST
def delete_template_item(request, item_id):
    """Supprimer un élément d'un repas type"""
    item = get_object_or_404(MealTemplateItem, id=item_id)
    template_id = item.template.id
    item.delete()
    messages.success(request, 'Élément supprimé du repas type.')
    return redirect('edit_meal_template', template_id=template_id)


@require_POST
def edit_template_item(request, item_id):
    """Modifier un élément d'un repas type (quantité)"""
    item = get_object_or_404(MealTemplateItem, id=item_id)
    template_id = item.template.id
    
    quantity = request.POST.get('quantity')
    if quantity:
        try:
            item.quantity = float(quantity)
            item.save()
            messages.success(request, 'Quantité mise à jour.')
        except ValueError:
            messages.error(request, 'Quantité invalide.')
    
    return redirect('edit_meal_template', template_id=template_id)


@require_POST
def apply_template(request, template_id):
    """Appliquer un repas type à une date donnée"""
    template = get_object_or_404(MealTemplate, id=template_id)
    date_str = request.POST.get('date')
    meal_type = request.POST.get('meal_type', template.meal_type)
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
    
    daily_entry, _ = DailyCalorieEntry.objects.get_or_create(date=selected_date)
    
    # Copier tous les éléments du template
    for template_item in template.template_items.all():
        MealItem.objects.create(
            daily_entry=daily_entry,
            food=template_item.food,
            meal_type=meal_type,
            quantity=template_item.quantity
        )
    
    messages.success(request, f'Repas type "{template.name}" appliqué!')
    return redirect('calories_dashboard_date', date_str=selected_date.strftime('%Y-%m-%d'))
