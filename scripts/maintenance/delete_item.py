import os
import sys
import django

# Add project root to sys.path to fix "ModuleNotFoundError"
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

from tracker.models import Food

def delete_poelee_test():
    # Search for "Accent" or "Test" since "poelee" might have accent issues in SQLite lookup
    targets_1 = Food.objects.filter(name__icontains="Accent")
    targets_2 = Food.objects.filter(name__icontains="Test")
    
    # Combine (union)
    targets = (targets_1 | targets_2).distinct()
    
    print(f"Scanning database for 'Accent' or 'Test'...")
    print(f"Found {targets.count()} potential matches:")
    
    deleted_count = 0
    for food in targets:
        print(f"- Found: '{food.name}' (ID: {food.id}, Brand: {food.brand})")
        
        # Check if it matches the user's target
        if "poêlée" in food.name.lower() or "poelee" in food.name.lower():
            print(f"  -> DELETING this item (matched 'Poêlée')")
            food.delete()
            deleted_count += 1
        elif "test" in food.name.lower() and "accent" in food.name.lower():
             print(f"  -> DELETING this item (matched 'Test' + 'Accent')")
             food.delete()
             deleted_count += 1
        else:
            print(f"  -> Skipping (preserving other data)")
            
    print(f"\nTotal deleted: {deleted_count}")

if __name__ == "__main__":
    delete_poelee_test()
