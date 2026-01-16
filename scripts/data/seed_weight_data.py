from datetime import date, timedelta
import random
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

from tracker.models import WeightEntry

def generate_specific_weight_data():
    print("Deleting existing weight data...")
    WeightEntry.objects.all().delete()
    
    start_date = date(2025, 9, 1)
    end_date = date.today()
    
    start_weight = 96.0
    end_weight = 85.4
    
    total_days = (end_date - start_date).days
    weight_loss = start_weight - end_weight
    daily_loss_avg = weight_loss / total_days
    
    current_weight = start_weight
    current_date = start_date
    
    # Body composition assumptions
    current_fat = 30.0 # Starting fat %
    current_muscle_mass = 38.0 
    
    entries = []
    
    print(f"Generating data from {start_date} ({start_weight}kg) to {end_date} ({end_weight}kg)...")
    
    for day in range(total_days + 1):
        # Add some noise to the linear trend
        noise = random.uniform(-0.3, 0.3)
        daily_loss = daily_loss_avg + random.uniform(-0.05, 0.05)
        
        # Calculate weight for the day (trending down + noise)
        target_weight_for_day = start_weight - (daily_loss_avg * day)
        final_weight = target_weight_for_day + noise
        
        # Ensure we hit the exact target on the last day? Or close enough.
        if day == total_days:
            final_weight = end_weight
        
        # Update body comp
        current_fat -= random.uniform(0, 0.05)
        current_muscle_mass += random.uniform(-0.01, 0.02) # Maintaining/Slight gain
        
        muscle_pct = (current_muscle_mass / final_weight) * 100
        visceral = max(1.0, (current_fat / 2.5))
        bmr = int(10 * final_weight + 6.25 * 184 - 5 * 30 + 5) 
        
        entries.append(WeightEntry(
            date=current_date,
            weight=round(final_weight, 2),
            body_fat_percentage=round(current_fat, 2),
            muscle_percentage=round(muscle_pct, 2),
            muscle_mass=round(current_muscle_mass, 2),
            visceral_fat=round(visceral, 1),
            basal_metabolic_rate=bmr
        ))
        
        current_date += timedelta(days=1)
    
    WeightEntry.objects.bulk_create(entries)
    print(f"Successfully created {len(entries)} weight entries.")

if __name__ == "__main__":
    generate_specific_weight_data()
