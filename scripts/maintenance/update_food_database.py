import os
import sys
import django

# Setup Django environment
# Current: scripts/maintenance/update_food_database.py
# Root is 3 levels up
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

from tracker.models import Food
from tracker.food_constants import GENERIC_FOODS

def update_foods():
    print("Updating food database...")
    count = 0
    
    # Mapping for renames: old_name -> new_name
    renames = {
        'Oeuf entier (cru)': 'Oeuf entier',
        'Avocat': 'Avocat (100g)'
    }

    # First handle renames
    for old_name, new_name in renames.items():
        try:
            food = Food.objects.get(name=old_name)
            food.name = new_name
            food.save()
            print(f"Renamed: {old_name} -> {new_name}")
        except Food.DoesNotExist:
            print(f"Note: {old_name} not found to rename (might already be renamed)")

    # Then update values based on new constants
    for item in GENERIC_FOODS:
        try:
            # Try to find by name (which might have just been updated)
            food = Food.objects.get(name=item['name'])
            
            # Update fields
            updated = False
            if food.calories != item['calories']:
                food.calories = item['calories']
                updated = True
            if food.protein != item['protein']:
                food.protein = item['protein']
                updated = True
            if food.carbs != item['carbs']:
                food.carbs = item['carbs']
                updated = True
            if food.fat != item['fat']:
                food.fat = item['fat']
                updated = True
            if food.fiber != item['fiber']:
                food.fiber = item['fiber']
                updated = True
            if food.serving_size != item['unit_weight']:
                food.serving_size = item['unit_weight']
                updated = True
                
            if updated:
                food.save()
                print(f"Updated values for: {food.name}")
                count += 1
                
        except Food.DoesNotExist:
            print(f"Creating new food: {item['name']}")
            Food.objects.create(
                name=item['name'],
                calories=item['calories'],
                protein=item['protein'],
                carbs=item['carbs'],
                fat=item['fat'],
                fiber=item['fiber'],
                serving_size=item['unit_weight']
            )
            count += 1

    print(f"Done. Updated/Created {count} items.")

if __name__ == '__main__':
    update_foods()
