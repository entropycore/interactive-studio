import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(BASE_DIR, 'data', 'assets_metadata.csv')

def get_art_wallpapers():
    wallpapers = []
    if os.path.exists(CSV_FILE):
        try:
            
            with open(CSV_FILE, mode='r', encoding='latin-1') as f:
                
                reader = csv.DictReader(f, delimiter=';')
                
                for row in reader:
                    fname = row.get('filename', '').strip()
                    if fname:
                        wallpapers.append({
                            "file": fname,
                            "title": row.get('title', 'Untitled'),
                            "artist": row.get('artist', 'Unknown'),
                            "year": row.get('year', 'Unknown'),
                            "movement": row.get('category', 'Classic'),
                            "museum": row.get('museum', 'Archive'),
                            "description": row.get('description', '')
                        })
            print(f"✅ CSV Loaded Successfully: {len(wallpapers)} items.")
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
    else:
        print(f"⚠️ CSV file not found at: {CSV_FILE}")
        
    return wallpapers