"""
Manual entry views for adding individual data points.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from tracker.models import GymSession
from tracker.forms import (
    WeightEntryForm, StepsEntryForm, ActivityEntryForm,
    GymSessionForm, CardioEntryForm, CaloriesEntryForm
)


def add_weight(request):
    """Ajouter une entrée de poids manuellement"""
    if request.method == 'POST':
        form = WeightEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Poids enregistré avec succès!')
            return redirect('dashboard')
    else:
        form = WeightEntryForm()
    
    return render(request, 'tracker/add_entry.html', {'form': form, 'title': 'Ajouter un poids'})


def add_steps(request):
    """Ajouter des pas manuellement"""
    if request.method == 'POST':
        form = StepsEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pas enregistrés avec succès!')
            return redirect('dashboard')
    else:
        form = StepsEntryForm()
    
    return render(request, 'tracker/add_entry.html', {'form': form, 'title': 'Ajouter des pas'})


def add_activity(request):
    """Ajouter une activité manuellement"""
    if request.method == 'POST':
        form = ActivityEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()
            # Si c'est de la musculation, ajouter une session de gym
            if entry.activity_type and entry.activity_type.upper() in ['MUSCULATION', 'TRAINING', 'GYM']:
                GymSession.objects.get_or_create(
                    date=entry.date, 
                    defaults={'notes': 'Ajout automatique depuis activité'}
                )

            messages.success(request, 'Activité enregistrée avec succès!')
            return redirect('dashboard')
    else:
        form = ActivityEntryForm()
    
    return render(request, 'tracker/add_entry.html', {'form': form, 'title': 'Ajouter une activité'})


def add_gym_session(request):
    """Ajouter ou modifier une séance de salle depuis le calendrier"""
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        
        if session_id:
            # Edit existing session
            session = get_object_or_404(GymSession, id=session_id)
            form = GymSessionForm(request.POST, instance=session)
            action = "modifiée"
        else:
            # Create new session
            # Check if session already exists for this date to prevent duplicates (white dot issue)
            date = request.POST.get('date')
            existing = GymSession.objects.filter(date=date).first()
            if existing:
                # Update the existing one instead of creating duplicate
                form = GymSessionForm(request.POST, instance=existing)
                action = "mise à jour (déjà existante)"
            else:
                form = GymSessionForm(request.POST)
                action = "enregistrée"

        if form.is_valid():
            form.save()
            messages.success(request, f'Séance de salle {action}!')
            return redirect('gym_calendar')
    else:
        form = GymSessionForm()
    
    return render(request, 'tracker/add_entry.html', {'form': form, 'title': 'Ajouter une séance de salle'})


@require_POST
def delete_gym_session_calendar(request):
    """Supprimer une séance depuis le calendrier"""
    session_id = request.POST.get('session_id')
    if session_id:
        session = get_object_or_404(GymSession, id=session_id)
        session.delete()
        messages.success(request, 'Séance supprimée.')
    return redirect('gym_calendar')


def add_cardio(request):
    """Ajouter ou modifier du cardio"""
    from tracker.models import CardioEntry
    
    if request.method == 'POST':
        form = CardioEntryForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            
            # Chercher une entrée existante pour cette date
            existing_entry = CardioEntry.objects.filter(date=date).first()
            
            if existing_entry:
                # Mettre à jour l'entrée existante
                existing_entry.treadmill_minutes = form.cleaned_data.get('treadmill_minutes', 0) or 0
                existing_entry.speed = form.cleaned_data.get('speed', 5.0) or 5.0
                existing_entry.notes = form.cleaned_data.get('notes', '')
                existing_entry.save()
                cardio = existing_entry
                action = "modifié"
            else:
                # Créer une nouvelle entrée
                cardio = form.save()
                action = "enregistré"
            
            # Calcul des pas pour la marche sur tapis
            if cardio.treadmill_minutes > 0:
                hours = cardio.treadmill_minutes / 60
                distance_km = cardio.speed * hours
                distance_m = distance_km * 1000
                stride_length_m = 1.84 * 0.415  # ~0.76m
                steps_added = int(distance_m / stride_length_m)
                messages.success(request, f'Cardio {action} ! {steps_added} pas (théoriques) seront affichés en plus.')
            else:
                messages.success(request, f'Cardio {action} !')
                
            return redirect('dashboard')
    else:
        form = CardioEntryForm()
    
    return render(request, 'tracker/add_entry.html', {'form': form, 'title': 'Ajouter du cardio'})


def add_calories(request):
    """Ajouter des calories (ancien modèle basique)"""
    if request.method == 'POST':
        form = CaloriesEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calories enregistrées!')
            return redirect('dashboard')
    else:
        form = CaloriesEntryForm()
    
    return render(request, 'tracker/add_entry.html', {'form': form, 'title': 'Ajouter des calories'})
