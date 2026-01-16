
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

import sys
sys.stdout.reconfigure(encoding='utf-8')
from tracker.models import Food

def update_db_baguette():
    print("Updating 'Pain (baguette)' in DB if exists...")
    try:
        f = Food.objects.get(name="Pain (baguette)")
        print(f"Found existing: {f.name} (ID: {f.id}) - Current Cals: {f.calories}")
        f.serving_size = 100
        f.calories = 276
        f.protein = 8.2
        f.carbs = 54.4
        f.fat = 1.6
        f.fiber = 3.8
        f.save()
        print(f"Updated {f.name} to 100g standards (276 kcal).")
    except Food.DoesNotExist:
        print("Pain (baguette) not found in DB. No DB update needed.")

if __name__ == "__main__":
    update_db_baguette()
