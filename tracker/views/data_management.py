"""
Data management views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from datetime import date, timedelta
import calendar

from tracker.models import (
    WeightEntry, StepsEntry, CardioEntry, GymSession, 
    ActivityEntry, CaloriesEntry
)
from tracker.forms import (
    WeightEntryForm, StepsEntryForm, CardioEntryForm,
    GymSessionForm, ActivityEntryForm, CaloriesEntryForm
)


def data_management(request):
    """Interface de gestion complète des données"""
    current_type = request.GET.get('type', 'weight')
    page_number = request.GET.get('page')
    
    if current_type == 'weight':
        queryset = WeightEntry.objects.all()
    elif current_type == 'steps':
        queryset = StepsEntry.objects.all()
    elif current_type == 'cardio':
        queryset = CardioEntry.objects.all()
    elif current_type == 'gym':
        queryset = GymSession.objects.all()
    elif current_type == 'activity':
        queryset = ActivityEntry.objects.all()
    elif current_type == 'calories':
        queryset = CaloriesEntry.objects.all()
    else:
        queryset = WeightEntry.objects.none()
    
    paginator = Paginator(queryset, 25)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'current_type': current_type,
        'page_obj': page_obj,
    }
    return render(request, 'tracker/data_management.html', context)


def edit_entry(request, entry_type, entry_id):
    """Editer une entrée spécifique"""
    model_map = {
        'weight': (WeightEntry, WeightEntryForm),
        'steps': (StepsEntry, StepsEntryForm),
        'cardio': (CardioEntry, CardioEntryForm),
        'gym': (GymSession, GymSessionForm),
        'activity': (ActivityEntry, ActivityEntryForm),
        'calories': (CaloriesEntry, CaloriesEntryForm),
    }
    
    if entry_type not in model_map:
        messages.error(request, "Type d'entrée inconnu.")
        return redirect('data_management')
    
    Model, FormClass = model_map[entry_type]
    entry = get_object_or_404(Model, id=entry_id)
    
    if request.method == 'POST':
        form = FormClass(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Entrée mise à jour.")
            return redirect(f"{reverse('data_management')}?type={entry_type}")
    else:
        form = FormClass(instance=entry)
    
    context = {
        'form': form,
        'title': "Modifier les données",
        'entry_type': entry_type,
    }
    return render(request, 'tracker/add_entry.html', context)


def delete_entry(request, entry_type, entry_id):
    """Supprimer une entrée"""
    model_map = {
        'weight': WeightEntry,
        'steps': StepsEntry,
        'cardio': CardioEntry,
        'gym': GymSession,
        'activity': ActivityEntry,
        'calories': CaloriesEntry
    }
    
    model = model_map.get(entry_type)
    if model:
        entry = get_object_or_404(model, id=entry_id)
        entry.delete()
        messages.success(request, "Entrée supprimée.")
    
    return redirect(f"{reverse('data_management')}?type={entry_type}")


@require_POST
def bulk_delete_entries(request):
    """Supprimer plusieurs entrées sélectionnées"""
    entry_type = request.POST.get('entry_type')
    selected_ids = request.POST.getlist('selected_ids')
    
    if not selected_ids:
        messages.warning(request, "Aucune entrée sélectionnée.")
        return redirect('data_management')

    model_map = {
        'weight': WeightEntry,
        'steps': StepsEntry,
        'cardio': CardioEntry,
        'gym': GymSession,
        'activity': ActivityEntry,
        'calories': CaloriesEntry
    }
    
    model = model_map.get(entry_type)
    
    if model:
        try:
            # Filtrer et supprimer les entrées
            deleted_count, _ = model.objects.filter(id__in=selected_ids).delete()
            messages.success(request, f"{deleted_count} entrée(s) supprimée(s) avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression : {str(e)}")
    else:
        messages.error(request, "Type d'entrée invalide.")
        
    return redirect(f"{reverse('data_management')}?type={entry_type}")


def gym_calendar(request):
    """Vue Calendrier annuel pour la salle de sport"""
    today = timezone.now().date()
    
    try:
        current_year = int(request.GET.get('year', today.year))
    except ValueError:
        current_year = today.year
    
    prev_year = current_year - 1
    next_year = current_year + 1
    
    # Récupérer toutes les séances de l'année
    start_date = date(current_year, 1, 1)
    end_date = date(current_year, 12, 31)
    sessions = GymSession.objects.filter(date__range=[start_date, end_date])
    
    # Mapper les sessions par date (peut y en avoir plusieurs par jour)
    sessions_map = {}
    for s in sessions:
        if s.date not in sessions_map:
            sessions_map[s.date] = []
        sessions_map[s.date].append({
            'type': s.session_type,
            'id': s.id
        })
        
    # Construire les données pour les 12 mois
    months_data = []
    for month in range(1, 13):
        cal = calendar.monthcalendar(current_year, month)
        month_weeks = []
        
        for week in cal:
            week_days = []
            for day in week:
                if day == 0:
                    week_days.append(None)
                else:
                    d = date(current_year, month, day)
                    week_days.append({
                        'day': day,
                        'date': d,
                        'is_today': d == today,
                        'sessions': sessions_map.get(d, [])
                    })
            month_weeks.append(week_days)
            
        months_data.append({
            'name': date(current_year, month, 1).strftime('%B'),
            'number': month,
            'weeks': month_weeks
        })

    # Calculer les stats pour l'année
    stats = {
        'PUSH': sessions.filter(session_type='PUSH').count(),
        'PULL': sessions.filter(session_type='PULL').count(),
        'UPPER': sessions.filter(session_type='UPPER').count(),
        'LOWER': sessions.filter(session_type='LOWER').count(),
    }

    context = {
        'current_year': current_year,
        'prev_year': prev_year,
        'next_year': next_year,
        'months_data': months_data,
        'today': today,
        'stats': stats,
    }
    return render(request, 'tracker/gym_calendar.html', context)
