from django.core.management.base import BaseCommand
from tracker.models import StepsEntry
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Import steps data from a text file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the data file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        with open(file_path, 'r') as f:
            lines = f.readlines()

        count_created = 0
        count_updated = 0
        count_skipped = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 2:
                self.stdout.write(self.style.WARNING(f'Skipping invalid line: {line}'))
                count_skipped += 1
                continue
            
            date_str = parts[0]
            steps_str = parts[1]

            try:
                # Parse date dd/mm
                day, month = map(int, date_str.split('/'))
                
                # Year logic: Step - Dec -> 2025, Jan -> 2026
                if month >= 9:
                    year = 2025
                else:
                    year = 2026
                
                date_obj = datetime(year, month, day).date()
                steps = int(steps_str)

                entry, created = StepsEntry.objects.update_or_create(
                    date=date_obj,
                    defaults={'steps': steps}
                )

                if created:
                    count_created += 1
                else:
                    count_updated += 1
                    
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f'Error parsing line "{line}": {e}'))
                count_skipped += 1

        self.stdout.write(self.style.SUCCESS(f'Import finished. Created: {count_created}, Updated: {count_updated}, Skipped: {count_skipped}'))
