import sqlite3
import zipfile
import os
import shutil

DB_PATH = 'data/fitness.db'
TEMP_DB_PATH = 'data/fitness_temp.db'
SQL_PATH = 'data/fitness_dump.sql'
ZIP_PATH = 'data/fitness_upload.zip'

def prepare_db():
    print(f"1. Creating temporary copy of database...")
    if not os.path.exists(DB_PATH):
        print("ERROR: Database file not found!")
        return
        
    shutil.copy2(DB_PATH, TEMP_DB_PATH)
    
    try:
        con = sqlite3.connect(TEMP_DB_PATH)
        cursor = con.cursor()
        
        # Check size of OFF table
        try:
            cursor.execute("SELECT count(*) FROM tracker_openfoodfacts_product")
            count = cursor.fetchone()[0]
            print(f"   Found {count} cached food items. Clearing them to save space...")
            
            # Clear the cache table to reduce size (it will be refilled automatically as used)
            cursor.execute("DELETE FROM tracker_openfoodfacts_product")
            con.commit()
            
            print("   Vacuuming database to reclaim space...")
            cursor.execute("VACUUM")
        except sqlite3.OperationalError:
            print("   Table tracker_openfoodfacts_product not found, skipping cleanup.")

        print(f"2. Dumping optimized database to {SQL_PATH}...")
        with open(SQL_PATH, 'w', encoding='utf-8') as f:
            for line in con.iterdump():
                f.write('%s\n' % line)
        con.close()
        
    except Exception as e:
        print(f"ERROR processing database: {e}")
        return
    finally:
        if os.path.exists(TEMP_DB_PATH):
            os.remove(TEMP_DB_PATH)

    # Zip the SQL file
    print(f"3. Compressing to {ZIP_PATH}...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(SQL_PATH, arcname='fitness_dump.sql')
        print(f"4. Compression complete!")
        print(f"\nCreated: {ZIP_PATH}")
        print(f"Size: {os.path.getsize(ZIP_PATH) / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"ERROR zipping file: {e}")
    finally:
        if os.path.exists(SQL_PATH):
            os.remove(SQL_PATH)

if __name__ == "__main__":
    prepare_db()
