import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/fitness.db')

def clean_duplicates():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Trouver les dates dupliquées
    cursor.execute("""
        SELECT date, COUNT(*) 
        FROM tracker_weightentry 
        GROUP BY date 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    
    total_removed = 0
    for date, count in duplicates:
        print(f"Found {count} entries for date {date}")
        
        # Récupérer les ids pour cette date, triés par id décroissant (supposons que id plus grand = plus récent)
        cursor.execute("SELECT id FROM tracker_weightentry WHERE date = ? ORDER BY id DESC", (date,))
        ids = [row[0] for row in cursor.fetchall()]
        
        # Garder le premier (le plus récent), supprimer les autres
        keep_id = ids[0]
        delete_ids = ids[1:]
        
        if delete_ids:
            placeholders = ','.join('?' * len(delete_ids))
            cursor.execute(f"DELETE FROM tracker_weightentry WHERE id IN ({placeholders})", delete_ids)
            total_removed += len(delete_ids)
            print(f"  Kept ID {keep_id}, removed IDs {delete_ids}")

    conn.commit()
    conn.close()
    print(f"Cleanup complete. Removed {total_removed} duplicate entries.")

if __name__ == "__main__":
    clean_duplicates()
