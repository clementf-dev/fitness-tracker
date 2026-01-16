import os
import sys
import django
from datetime import date

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

from tracker.models import GymSession

def set_sessions():
    year = 2026
    
    # 9 Jan -> LOWER
    d9 = date(year, 1, 9)
    GymSession.objects.filter(date=d9).delete() # Clear existing to avoid duplicates
    GymSession.objects.create(date=d9, session_type='LOWER')
    print(f"Set {d9} to LOWER")

    # 10 Jan -> PUSH
    d10 = date(year, 1, 10)
    GymSession.objects.filter(date=d10).delete() # Clear existing
    GymSession.objects.create(date=d10, session_type='PUSH')
    print(f"Set {d10} to PUSH")

if __name__ == '__main__':
    set_sessions()
