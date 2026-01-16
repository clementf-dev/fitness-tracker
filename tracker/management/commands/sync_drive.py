import os
import csv
import io
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from tracker.models import WeightEntry, StepsEntry

# Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCPES = ['https://www.googleapis.com/auth/drive.readonly']

class Command(BaseCommand):
    help = 'Synchronize fitness data from Google Drive'

    def handle(self, *args, **options):
        self.stdout.write("Starting Drive Sync...")
        
        creds = self.authenticate()
        service = build('drive', 'v3', credentials=creds)
        
        self.sync_weight(service)
        self.sync_steps(service)
        
        self.stdout.write(self.style.SUCCESS('Sync Complete!'))

    def authenticate(self):
        """Authenticate with Google Drive"""
        creds = None
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCPES)
            
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    self.stdout.write(self.style.ERROR('ERROR: credentials.json not found! Please download OAuth Client ID JSON from Cloud Console and save it as credentials.json in the project root.'))
                    return None
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCPES)
                creds = flow.run_local_server(port=0)
                
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
        return creds

    def sync_weight(self, service):
        """Find and parse weight_data.csv"""
        self.stdout.write("Searching for weight_data.csv...")
        
        # Search for file
        results = service.files().list(
            q="name = 'weight_data.csv' and trashed = false",
            pageSize=1, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            self.stdout.write(self.style.WARNING('weight_data.csv not found.'))
            return

        file_id = items[0]['id']
        content = self.download_file(service, file_id)
        
        if content:
            self.parse_weight_csv(content)

    def sync_steps(self, service):
        """Find and parse steps_data.csv"""
        self.stdout.write("Searching for steps_data.csv...")
        
        # Search for file
        results = service.files().list(
            q="name = 'steps_data.csv' and trashed = false",
            pageSize=1, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            self.stdout.write(self.style.WARNING('steps_data.csv not found.'))
            return

        file_id = items[0]['id']
        content = self.download_file(service, file_id)
        
        if content:
            self.parse_steps_csv(content)

    def download_file(self, service, file_id):
        """Download file content as string"""
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        return fh.getvalue().decode('utf-8')

    def parse_weight_csv(self, content):
        """Parse Weight CSV and update DB"""
        # Format: Date,Heure,Poids,Fat%,FatMass,FFM%,FFM,SkelMusc%,SkelMusc,Musc%,MuscMass,Bone,Water,BMR
        # Example: 2026.01.16 01:45:00,01:45:00,80.0,20.0,16.0,80.0,64.0,0.0,0.0,40.0,32.0,3.5,45.0,1800
        
        csv_reader = csv.reader(io.StringIO(content))
        header = next(csv_reader, None) # Skip header
        
        count = 0
        for row in csv_reader:
            if not row or len(row) < 3: continue
            
            try:
                # Indices based on CsvExporter.kt
                # 0: Date, 1: Time, 2: Weight
                # 3: BF%, 4: BFMass
                # 9: Muscle%, 10: MuscleMass
                # 11: BoneMass
                # 12: WaterMass
                # 13: BMR
                
                date_str = row[0]
                weight_str = row[2]
                
                bf_str = row[3] if len(row) > 3 else None
                muscle_pct_str = row[9] if len(row) > 9 else None
                muscle_mass_str = row[10] if len(row) > 10 else None
                bone_str = row[11] if len(row) > 11 else None
                water_str = row[12] if len(row) > 12 else None
                bmr_str = row[13] if len(row) > 13 else None
                visceral_str = row[14] if len(row) > 14 else None
                
                dt = datetime.datetime.strptime(date_str, "%Y.%m.%d %H:%M:%S")
                dt = timezone.make_aware(dt)
                
                weight = float(weight_str.replace(',', '.'))
                
                defaults = {
                    'time': dt.time(),
                    'weight': weight
                }
                
                # Helper for safe float conversion
                def safe_float(val):
                    if not val or val == '0.0' or val == '0': return None
                    try: return float(val.replace(',', '.'))
                    except: return None
                
                defaults['body_fat_percentage'] = safe_float(bf_str)
                defaults['muscle_percentage'] = safe_float(muscle_pct_str)
                defaults['muscle_mass'] = safe_float(muscle_mass_str)
                defaults['bone_mass'] = safe_float(bone_str)
                defaults['body_water'] = safe_float(water_str)
                defaults['visceral_fat'] = safe_float(visceral_str)
                
                bmr_val = safe_float(bmr_str)
                if bmr_val: defaults['basal_metabolic_rate'] = int(bmr_val)
                
                obj, created = WeightEntry.objects.update_or_create(
                    date=dt.date(),
                    defaults=defaults
                )
                if created: count += 1
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error parsing row {row}: {e}"))
                
        self.stdout.write(self.style.SUCCESS(f"Imported/Updated weight entries. New: {count}"))

    def parse_steps_csv(self, content):
        """Parse Steps CSV and update DB"""
        # Format: Date,Heure,Pas
        # Example: 2025.12.01 06:22:32,06:22:32,1098
        
        csv_reader = csv.reader(io.StringIO(content))
        header = next(csv_reader, None) # Skip header
        
        count = 0
        for row in csv_reader:
            if not row or len(row) < 3: continue
            
            try:
                date_str = row[0]
                steps_str = row[2]
                
                dt = datetime.datetime.strptime(date_str, "%Y.%m.%d %H:%M:%S")
                dt = timezone.make_aware(dt)
                
                steps = int(steps_str)
                
                obj, created = StepsEntry.objects.update_or_create(
                    date=dt.date(),
                    defaults={
                        'time': dt.time(),
                        'steps': steps
                    }
                )
                if created: count += 1
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error parsing row {row}: {e}"))
                
        self.stdout.write(self.style.SUCCESS(f"Imported {count} new steps entries."))
