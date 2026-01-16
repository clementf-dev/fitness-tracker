"""
Dashboard views for the fitness tracker.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg
from django.utils import timezone
from django.views.decorators.http import require_GET
from datetime import timedelta, date

from tracker.models import (
    WeightEntry, StepsEntry, GymSession, CardioEntry, DailyCalorieEntry
)


def dashboard(request):
    """Dashboard principal avec statistiques et graphiques"""
    # Statistiques récentes
    latest_weight = WeightEntry.objects.first()
    
    # Moyenne des pas sur 30 jours
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    avg_steps = StepsEntry.objects.filter(date__gte=thirty_days_ago).aggregate(Avg('steps'))['steps__avg']
    
    total_gym_sessions = GymSession.objects.count()
    
    # Get yesterday's calories from DailyCalorieEntry model
    yesterday = timezone.now().date() - timedelta(days=1)
    yesterday_entry = DailyCalorieEntry.objects.filter(date=yesterday).first()
    yesterday_total_calories = yesterday_entry.total_calories if yesterday_entry else 0

    context = {
        'latest_weight': latest_weight,
        'avg_steps': int(avg_steps) if avg_steps else 0,
        'total_gym_sessions': total_gym_sessions,
        'yesterday_calories': yesterday_total_calories,
        'yesterday_date': yesterday,
    }
    return render(request, 'tracker/dashboard.html', context)


@require_GET
def api_combined_data(request):
    """API unifiée pour le graphique combiné"""
    range_type = request.GET.get('range', '30d')  # 7d, 30d, 3m, all
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)  # Default
    
    if range_type == '7d':
        start_date = end_date - timedelta(days=7)
    elif range_type == '30d':
        start_date = end_date - timedelta(days=30)
    elif range_type == '3m':
        start_date = end_date - timedelta(days=90)
    elif range_type == 'all':
        first_entry = WeightEntry.objects.order_by('date').first()
        if first_entry:
            start_date = first_entry.date
        else:
            start_date = end_date - timedelta(days=365)

    # Steps data
    steps_qs = StepsEntry.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')
    steps_dict = {s.date: s.steps for s in steps_qs}

    # Cardio steps (from treadmill)
    cardio_qs = CardioEntry.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')
    cardio_dict = {}
    for c in cardio_qs:
        if c.treadmill_minutes > 0:
            hours = c.treadmill_minutes / 60
            distance_km = c.speed * hours
            distance_m = distance_km * 1000
            stride_length_m = 1.84 * 0.415
            cardio_steps = int(distance_m / stride_length_m)
            cardio_dict[c.date] = cardio_steps

    # Weight and other body metrics
    weights_qs = WeightEntry.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')
    metrics_dict = {}
    for w in weights_qs:
        metrics_dict[w.date] = {
            'weight': float(w.weight),
            'body_fat': float(w.body_fat_percentage) if w.body_fat_percentage else None,
            'muscle_pct': float(w.muscle_percentage) if w.muscle_percentage else None,
            'muscle_mass': float(w.muscle_mass) if w.muscle_mass else None,
            'visceral_fat': float(w.visceral_fat) if w.visceral_fat else None,
            'bmr': float(w.basal_metabolic_rate) if w.basal_metabolic_rate else None,
        }

    cal_qs = DailyCalorieEntry.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')
    cal_dict = {c.date: c.total_calories for c in cal_qs}

    # Gym sessions
    gym_sessions = GymSession.objects.filter(date__gte=start_date, date__lte=end_date)
    gym_map = {s.date: s.session_type for s in gym_sessions}

    # Build day-by-day data
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)

    labels = []
    weight_data = []
    
    # Extended Metrics
    body_fat_data = []
    muscle_pct_data = []
    muscle_mass_data = []
    visceral_fat_data = []
    bmr_data = []
    
    steps_total_data = []
    steps_cardio_data = []
    calories_data = []
    gym_types_data = []

    last_known_weight = None
    
    # Find last known weight before period for initialization
    prior_weight = WeightEntry.objects.filter(date__lt=start_date).order_by('-date').first()
    if prior_weight:
        last_known_weight = prior_weight.weight

    for d in dates:
        labels.append(d.strftime('%d/%m'))
        
        steps_total_data.append(steps_dict.get(d, 0))
        steps_cardio_data.append(cardio_dict.get(d, 0))
        
        # Weight & Extended Metrics
        m = metrics_dict.get(d)
        if m:
            last_known_weight = m['weight']
            weight_data.append(m['weight'])
            body_fat_data.append(m['body_fat'])
            muscle_pct_data.append(m['muscle_pct'])
            muscle_mass_data.append(m['muscle_mass'])
            visceral_fat_data.append(m['visceral_fat'])
            bmr_data.append(m['bmr'])
        else:
            weight_data.append(last_known_weight)
            body_fat_data.append(None)
            muscle_pct_data.append(None)
            muscle_mass_data.append(None)
            visceral_fat_data.append(None)
            bmr_data.append(None)
            
        calories_data.append(cal_dict.get(d, None))
        gym_types_data.append(gym_map.get(d, None))

    return JsonResponse({
        'labels': labels,
        'steps': steps_total_data,
        'steps_cardio': steps_cardio_data,
        'weight': weight_data,
        'body_fat': body_fat_data,
        'muscle_pct': muscle_pct_data,
        'muscle_mass': muscle_mass_data,
        'visceral_fat': visceral_fat_data,
        'bmr': bmr_data,
        'calories': calories_data,
        'gym_days': gym_types_data
    })
