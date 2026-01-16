
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

import sys
sys.stdout.reconfigure(encoding='utf-8')
from tracker.models import Food, GenericFood

def list_foods():
    print("Listing first 20 Food items...")
    foods = Food.objects.all()[:20]
    if not foods:
        print("No Food items found at all.")
    for f in foods:
         print(f"ID: {f.id} | Name: '{f.name}'")

    print("\nListing first 20 GenericFood items...")
    generics = GenericFood.objects.all()[:20]
    if not generics:
        print("No GenericFood items found.")
    for g in generics:
        print(f"ID: {g.id} | Name: '{g.name}'")

if __name__ == "__main__":
    list_foods()
