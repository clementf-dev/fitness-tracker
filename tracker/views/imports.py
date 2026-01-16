"""
CSV import views.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
import csv
import io

from tracker.models import WeightEntry, StepsEntry, ActivityEntry, GymSession
from tracker.forms import CSVUploadForm


def import_csv(request):
    """Import de fichiers CSV"""
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_type = form.cleaned_data['csv_type']
            csv_file = request.FILES['csv_file']
            
            try:
                # Lire le fichier CSV
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                count = 0
                if csv_type == 'weight':
                    count = import_weight_csv(reader)
                elif csv_type == 'steps':
                    count = import_steps_csv(reader)
                elif csv_type == 'activities':
                    count = import_activities_csv(reader)
                
                messages.success(request, f'{count} entrées importées avec succès!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'import: {str(e)}')
    else:
        form = CSVUploadForm()
    
    return render(request, 'tracker/import_csv.html', {'form': form})


def sync_from_drive_view(request):
    """Sync CSV files from Google Drive FitSync folder"""
    from tracker.services.drive_sync import sync_from_drive
    
    if request.method == 'POST':
        result = sync_from_drive()
        
        if result.get('success'):
            messages.success(
                request, 
                f"Sync réussie! {result['weight_entries']} poids, {result['steps_entries']} pas importés."
            )
        else:
            messages.error(request, f"Erreur: {result.get('error', 'Unknown error')}")
        
        return redirect('dashboard')
    
    return render(request, 'tracker/sync_drive.html')


def import_weight_csv(reader):
    """Importer les données de poids depuis CSV"""
    count = 0
    for row in reader:
        try:
            # Parser la date au format "2026.01.07 11:33:25"
            date_str = row.get('Date', '')
            time_str = row.get('Heure', '')
            
            if not date_str:
                continue
            
            # Convertir le format de date
            if ' ' in date_str:  # Format "YYYY.MM.DD HH:MM:SS"
                date_obj = datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S').date()
                time_obj = datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S').time()
            else:
                date_obj = datetime.strptime(date_str, '%Y.%m.%d').date()
                time_obj = datetime.strptime(time_str, '%H:%M:%S').time() if time_str else datetime.now().time()

            
            # Créer ou mettre à jour l'entrée
            weight_data = {
                'date': date_obj,
                'time': time_obj,
                'weight': float(row.get('Poids', 0).replace(',', '.')) if row.get('Poids') else 0,
                'body_fat_percentage': float(row.get('Pourcentage de graisse corporelle', 0).replace(',', '.')) if row.get('Pourcentage de graisse corporelle') else None,
            }
            
            WeightEntry.objects.update_or_create(
                date=date_obj,
                time=time_obj,
                defaults=weight_data
            )
            count += 1
        except Exception as e:
            print(f"Erreur ligne poids: {e}")
            continue
    
    return count


def import_steps_csv(reader):
    """Importer les données de pas depuis CSV"""
    count = 0
    daily_steps = {}

    # 1. Agréger les pas par date
    for row in reader:
        try:
            date_str = row.get('Date', '')
            
            if not date_str:
                continue
                
            if ' ' in date_str:
                date_obj = datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S').date()
            else:
                date_obj = datetime.strptime(date_str, '%Y.%m.%d').date()
            
            steps = int(row.get('Pas', 0))
            
            if date_obj in daily_steps:
                daily_steps[date_obj] += steps
            else:
                daily_steps[date_obj] = steps
                
        except Exception as e:
            print(f"Erreur ligne pas: {e}")
            continue

    # 2. Sauvegarder les totaux
    for date_obj, total_steps in daily_steps.items():
        StepsEntry.objects.update_or_create(
            date=date_obj,
            defaults={'steps': total_steps}
        )
        count += 1
    
    return count


def import_activities_csv(reader):
    """Importer les données d'activités depuis CSV (HealthSync ou Strong)"""
    count = 0
    for row in reader:
        try:
            # Détection du format (HealthSync vs Strong)
            source_app = row.get('Application source', '')
            is_strong = 'strongapp' in source_app or 'unknown-io.strongapp.strong' in row.values()
            
            date_str = row.get('Date', '')
            time_str = row.get('Heure', '')
            
            if not date_str:
                continue

            if ' ' in date_str:
                dt = datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S')
                date_obj = dt.date()
                time_obj = dt.time()
            else:
                date_obj = datetime.strptime(date_str, '%Y.%m.%d').date()
                time_obj = datetime.strptime(time_str, '%H:%M:%S').time() if time_str else datetime.now().time()
            
            activity_data = {
                'date': date_obj,
                'time': time_obj,
                'source_app': source_app,
                'activity_type': row.get('Type d\'activité', ''),
                'activity_name': row.get('Nom de l\'activité', ''),
                'distance_km': float(row.get('Distance (km)', 0).replace(',', '.')) if row.get('Distance (km)') else None,
            }
            
            ActivityEntry.objects.create(**activity_data)
            
            # Si c'est un entraînement Strong, on crée aussi une GymSession
            if is_strong or activity_data['activity_type'] == 'TRAINING':
                GymSession.objects.get_or_create(
                    date=date_obj,
                    defaults={'notes': f"Importé depuis {source_app}"}
                )
            
            count += 1
        except Exception as e:
            print(f"Erreur ligne activité: {e}")
            continue
    
    return count
