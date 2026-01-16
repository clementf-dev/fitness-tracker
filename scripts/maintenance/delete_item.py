import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

from tracker.models import Food

def delete_poelee_test():
    # Case insensitive search for "poelee test"
    # Or strict if known. User said "poelee test".
    
    deleted_count = 0
    
    # Try exact or contains
    targets = Food.objects.filter(name__icontains="poelee test")
    
    print(f"Found {targets.count()} item(s) to delete:")
    for food in targets:
        print(f"- Deleting: {food.name} (ID: {food.id})")
        food.delete()
        deleted_count += 1
        
    print(f"\nTotal deleted: {deleted_count}")

if __name__ == "__main__":
    delete_poelee_test()
