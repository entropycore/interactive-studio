import os
import json

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'static', 'wallpapers')
DATA_FILE = os.path.join(BASE_DIR, 'data', 'assets.json') 

def load_assets():
    if not os.path.exists(os.path.dirname(DATA_FILE)):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
            return []
    
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_assets(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_art_wallpapers():
    supported_ext = ('.jpg', '.jpeg', '.png', '.webp')
    
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR, exist_ok=True)
        return []

    
    files_on_disk = [f for f in os.listdir(ASSETS_DIR) if f.lower().endswith(supported_ext)]
    current_data = load_assets()
    
    
    current_data = [item for item in current_data if item['file'] in files_on_disk]
    
    registered_files = [item['file'] for item in current_data]
    new_changes = False
    
    
    for filename in files_on_disk:
        if filename not in registered_files:
            
            clean_title = filename.split('.')[0].replace('-', ' ').replace('_', ' ').title()
            
            new_entry = {
                "id": len(current_data) + 1,
                "file": filename,
                "title": clean_title,
                "artist": "Unknown Artist",
                "year": "Unknown",
                "movement": "Classic Art", 
                "museum": "Digital Archive"
            }
            current_data.append(new_entry)
            new_changes = True

    if new_changes or len(current_data) != len(load_assets()):
        save_assets(current_data)
        
    return current_data