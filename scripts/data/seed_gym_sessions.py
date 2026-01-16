import os
import django
from datetime import date

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

from tracker.models import GymSession

def seed_sessions():
    # Données fournies
    sessions_data = {
        'PUSH': {
            'Septembre': [7, 11, 15, 19, 22, 27],
            'Octobre': [1, 5, 8, 12, 20, 23, 26, 29],
            'Novembre': [2, 5, 8, 11, 15, 18, 23, 28],
            'Décembre': [3, 7, 13, 18]
        },
        'PULL': {
            'Septembre': [4, 8, 12, 16, 20, 24, 28],
            'Octobre': [2, 6, 9, 14, 21, 25, 31],
            'Novembre': [4, 9, 13, 17, 20, 24, 29],
            'Décembre': [6, 14, 19]
        },
        'LOWER': {
            'Septembre': [17, 23, 29],
            'Octobre': [3, 10, 13, 27],
            'Novembre': [1, 6, 10, 16, 30],
            'Décembre': [4, 8, 15, 20],
            'Janvier': [6]
        },
        'UPPER': {
            'Octobre': [16, 18],
            'Décembre': [22],
            'Janvier': [4, 7]
        }
    }

    month_map = {
        'Septembre': 9,
        'Octobre': 10,
        'Novembre': 11,
        'Décembre': 12,
        'Janvier': 1
    }

    count = 0
    for session_type, months in sessions_data.items():
        for month_name, days in months.items():
            month_num = month_map[month_name]
            
            # Logique année: Sept-Dec = 2025, Jan = 2026
            year = 2026 if month_num in [1, 2] else 2025

            for day in days:
                session_date = date(year, month_num, day)
                obj, created = GymSession.objects.get_or_create(
                    date=session_date,
                    defaults={'session_type': session_type}
                )
                if created:
                    count += 1
                    print(f"Created {session_type} on {session_date}")
                else:
                    # Update type if exists (user might want to correct it)
                    if obj.session_type != session_type:
                        obj.session_type = session_type
                        obj.save()
                        print(f"Updated {session_type} on {session_date}")
                    else:
                        print(f"Skipped {session_type} on {session_date} (Already exists)")

    print(f"\nTotal sessions created: {count}")

if __name__ == '__main__':
    seed_sessions()
