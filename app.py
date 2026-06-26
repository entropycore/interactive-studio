from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import uuid
import base64
import json
import shutil 
from datetime import datetime
from werkzeug.utils import secure_filename
from modules.generative_art import StudioArtGenerator

# --- IMPORTS MODULES ---
from modules.data_viz import DataAnalyzer 
try:
    from modules.media_tools import MediaProcessor
except ImportError:
    MediaProcessor = None

# Import AI Logic
from modules.ai_assistant import ArtAssistant
from modules.assets_manager import get_art_wallpapers




app = Flask(__name__)

# --- CONFIGURATION ---
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'
app.config['CHATS_FILE'] = 'data/chats.json'
app.config['NOTES_FILE'] = 'data/creative_notes.json'
app.secret_key = 'super_secret_key'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# --- HONAR AI ENGINE START (Global for Speed) ---
print(" Starting Honar AI Engine...")
try:
    bot_engine = ArtAssistant()
    print(" Honar is Online and Ready!")
except Exception as e:
    print(f"⚠️ Error starting Honar: {e}")
    bot_engine = None

# --- HELPERS ---
def load_chats():
    if not os.path.exists(app.config['CHATS_FILE']):
        return []
    with open(app.config['CHATS_FILE'], 'r') as f:
        try:
            return json.load(f)
        except:
            return []

def save_chats(chats):
    with open(app.config['CHATS_FILE'], 'w') as f:
        json.dump(chats, f, indent=4)

def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions

def load_notes():
    if not os.path.exists(app.config['NOTES_FILE']):
        return []
    with open(app.config['NOTES_FILE'], 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_notes(notes):
    with open(app.config['NOTES_FILE'], 'w', encoding='utf-8') as f:
        json.dump(notes, f, indent=2)

# ==========================================
#  ROUTES: DATA VISUALIZATION
# ==========================================

@app.route('/data-art')
def data_art():
    return render_template('data_art.html')

@app.route('/api/analyze-csv', methods=['POST'])
def analyze_csv():
    if 'csv_file' not in request.files:
        return jsonify({"success": False, "error": "Choose a CSV file before analyzing."}), 400
    
    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({"success": False, "error": "The selected file has no filename."}), 400

    if not allowed_file(file.filename, {'csv'}):
        return jsonify({"success": False, "error": "Only CSV files are supported in Data Art."}), 400

    filename = secure_filename(file.filename)
    filename = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        analyzer = DataAnalyzer(app.config['UPLOAD_FOLDER'])

        result = analyzer.process_and_suggest(filename)
        status = 200 if result.get("success") else 422
        return jsonify(result), status
    except Exception as e:
        print(f"CSV analysis failed: {e}")
        return jsonify({"success": False, "error": "The CSV could not be analyzed. Check formatting and try again."}), 500

# ==========================================
#  ROUTES: CHAT SYSTEM
# ==========================================

@app.route('/honar')
def honar():
    chats = load_chats()
    chats.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return render_template('honar.html', chats=chats)

@app.route('/api/chat/new', methods=['POST'])
def new_chat():
    chats = load_chats()
    chat_id = str(uuid.uuid4())
    new_session = {
        "id": chat_id,
        "title": "New Conversation",
        "timestamp": datetime.now().isoformat(),
        "messages": [{"sender": "bot", "text": "Hello! I am Honar. How can I help you create art today? "}]
    }
    chats.append(new_session)
    save_chats(chats)
    return jsonify(new_session)

@app.route('/api/chat/get/<chat_id>')
def get_chat(chat_id):
    chats = load_chats()
    chat = next((c for c in chats if c['id'] == chat_id), None)
    return jsonify(chat)

@app.route('/api/chat/send', methods=['POST'])
def send_message():
    data = request.json
    chat_id = data.get('chat_id')
    user_msg = data.get('message')
    chats = load_chats()
    session = next((c for c in chats if c['id'] == chat_id), None)
    
    if session:
        session['messages'].append({"sender": "user", "text": user_msg})
        if session['title'] == "New Conversation":
            session['title'] = user_msg[:20] + "..." if len(user_msg) > 20 else user_msg
            
        try:
            if bot_engine:
                bot_response = bot_engine.get_response(user_msg)
            else:
                temp_bot = ArtAssistant()
                bot_response = temp_bot.get_response(user_msg)
        except Exception as e:
            bot_response = "Honar is recalibrating... (Use standard model for faster response)."
            print(f"Error generating response: {e}")

        session['messages'].append({"sender": "bot", "text": bot_response})
        session['timestamp'] = datetime.now().isoformat()
        save_chats(chats)
        return jsonify({"response": bot_response})
    
    return jsonify({"error": "Chat not found"}), 404

@app.route('/api/chat/delete', methods=['POST'])
def delete_chat():
    data = request.json
    chat_id = data.get('chat_id')
    chats = load_chats()
    new_chats = [c for c in chats if c['id'] != chat_id]
    if len(new_chats) < len(chats):
        save_chats(new_chats)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Chat not found"}), 404

# --- ⚠️ ADDED BACK: WIDGET ROUTE (Safety Net) ---
@app.route('/chat', methods=['POST'])
def chat_widget():
   
    try:
        user_message = request.json.get('message')
        if bot_engine:
            response = bot_engine.get_response(user_message)
        else:
            temp_bot = ArtAssistant()
            response = temp_bot.get_response(user_message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"response": "Error connecting to Honar."})

# ==========================================
#  OTHER ROUTES
# ==========================================

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/gallery')
def gallery():
    files = []
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        files = os.listdir(app.config['OUTPUT_FOLDER'])
        files.sort(key=lambda x: os.path.getmtime(os.path.join(app.config['OUTPUT_FOLDER'], x)), reverse=True)
    
    drawings = [f for f in files if f.startswith('drawing_')]
    saved_assets = [f for f in files if f.startswith('saved_')]
    data_art = [f for f in files if f.startswith(('chart_', 'data_', 'wave_'))]
    edited = [f for f in files if f.startswith('edited_')]
    
    return render_template('gallery.html', drawings=drawings, saved_assets=saved_assets, data_art=data_art, edited=edited)

@app.route('/delete_image', methods=['POST'])
def delete_image():
    try:
        data = request.json
        filename = data.get('filename')
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/generative', methods=['GET', 'POST'])
def generative():
    saved_image = None
    if request.method == 'POST':
        
        image_data = request.form.get('image_data')
        if image_data:
            image_data = image_data.replace('data:image/png;base64,', '')
            filename = f"drawing_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            with open(filepath, "wb") as f: 
                f.write(base64.b64decode(image_data))
            saved_image = filename
            
        
        style = request.form.get('style')
        theme = request.form.get('theme')
        
        if style and theme:
            
            art_studio = GenerativeArt(width=1200, height=800, theme=theme)
            
           
            if style == "chaos":
                art_studio.generate_geometric_chaos(150)
            elif style == "grid":
                art_studio.generate_abstract_grid(12)
            elif style == "network":
                art_studio.generate_network_nodes(100)
            
         
            saved_image = art_studio.save_image(app.config['OUTPUT_FOLDER'])

    return render_template('generative.html', saved_image=saved_image)

@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/api/media/image', methods=['POST'])
def api_media_image():
    if MediaProcessor is None:
        return jsonify({"success": False, "error": "Media processing is unavailable."}), 503
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Upload an image first."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "The selected image has no filename."}), 400
    if not allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'webp'}):
        return jsonify({"success": False, "error": "Use a PNG, JPG, JPEG, or WEBP image."}), 400

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        processor = MediaProcessor(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'])
        output = processor.process_image(filename, request.form.get('filter_type', 'edge'))
        if not output:
            return jsonify({"success": False, "error": "The uploaded file could not be opened as an image."}), 422
        return jsonify({
            "success": True,
            "filename": output,
            "url": url_for('static', filename=f'outputs/{output}')
        })
    except Exception as e:
        print(f"Image processing failed: {e}")
        return jsonify({"success": False, "error": "Image processing failed. Try a different file."}), 500

@app.route('/api/media/audio', methods=['POST'])
def api_media_audio():
    if MediaProcessor is None:
        return jsonify({"success": False, "error": "Media processing is unavailable."}), 503
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Upload an audio file first."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "The selected audio file has no filename."}), 400
    if not allowed_file(file.filename, {'wav', 'mp3'}):
        return jsonify({"success": False, "error": "Use a WAV or MP3 audio file."}), 400

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        processor = MediaProcessor(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'])
        output = processor.process_audio(filename, request.form.get('effect_type', 'reverb'))
        return jsonify({
            "success": True,
            "filename": output,
            "url": url_for('static', filename=f'outputs/{output}')
        })
    except Exception as e:
        print(f"Audio processing failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==========================================
#  ROUTES: WORKSPACE DASHBOARD & EDITOR
# ==========================================

@app.route('/notes')
def notes_dashboard():
    # Render the dashboard with all saved workspaces
    notes = load_notes()
    return render_template('notes.html', notes=notes)

@app.route('/editor', defaults={'note_id': None})
@app.route('/editor/<note_id>')
def editor(note_id):
    # Redirect to dashboard if accessed without an ID
    if not note_id:
        return redirect(url_for('notes_dashboard'))
        
    # Load specific workspace data
    notes = load_notes()
    note = next((n for n in notes if n.get('id') == note_id), None)
    if not note:
        return redirect(url_for('notes_dashboard'))
        
    return render_template('editor.html', note=note)

@app.route('/api/notes/create', methods=['POST'])
def create_note():
    # Initialize a new canvas
    data = request.json
    notes = load_notes()
    note_id = uuid.uuid4().hex[:8]
    
    new_note = {
        "id": note_id,
        "title": data.get('title', 'Untitled Canvas'),
        "content": "",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    notes.insert(0, new_note)
    save_notes(notes)
    return jsonify({"success": True, "note_id": note_id})

@app.route('/api/notes/delete/<note_id>', methods=['POST'])
def delete_note(note_id):
    # Delete a workspace by ID
    notes = load_notes()
    notes = [n for n in notes if n.get('id') != note_id]
    save_notes(notes)
    return jsonify({"success": True})

@app.route('/api/notes/save/<note_id>', methods=['POST'])
def save_note_content(note_id):
    # Save DOM content of the active workspace
    data = request.json
    notes = load_notes()
    
    for note in notes:
        if note.get('id') == note_id:
            note['content'] = data.get('content', '')
            note['updated_at'] = datetime.now().isoformat()
            break
            
    save_notes(notes)
    return jsonify({"success": True})

@app.route('/assets')
def assets():
    wallpapers_data = get_art_wallpapers()
    return render_template('assets.html', wallpapers=wallpapers_data)

@app.route('/api/add-to-gallery', methods=['POST'])
def add_to_gallery():
    data = request.json
    filename = data.get('filename')
    source_path = os.path.join('static', 'wallpapers', filename)
    new_filename = f"saved_{uuid.uuid4().hex}_{filename}"
    dest_path = os.path.join(app.config['OUTPUT_FOLDER'], new_filename)
    if os.path.exists(source_path):
        shutil.copy(source_path, dest_path)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 404

# --- SEARCH & CONTACT ---
SITE_CONTENT = [
    {"title": "Home", "url": "/", "keywords": "start, main, index, home"},
    {"title": "Sketch Pad", "url": "/generative", "keywords": "draw, art, paint, canvas, creative, sketch"},
    {"title": "Gallery", "url": "/gallery", "keywords": "images, saved, portfolio, work, art"},
    {"title": "Data Visualization", "url": "/data-art", "keywords": "charts, pandas, graph, data, analysis, csv"},
    {"title": "Media Tools", "url": "/tools", "keywords": "filter, image, edit, blur, grayscale, process"},
    {"title": "Notes Editor", "url": "/editor", "keywords": "text, write, memo, draft, ideas"},
    {"title": "Assets", "url": "/assets", "keywords": "resources, images, background, download"},
    {"title": "Honar AI", "url": "/honar", "keywords": "chat, ai, bot, assistant, help, artificial"}
]

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    if not query: return jsonify([])
    results = [item for item in SITE_CONTENT if query in item['title'].lower() or query in item['keywords']]
    return jsonify(results[:5])

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message') 
        
        if not name or not email or not message:
            flash("Please fill all fields!", "error")
            return redirect(url_for('contact'))
            
        
        data = {"name": name, "email": email, "message": message, "date": datetime.now().isoformat()}
        try:
            messages_path = os.path.join('data', 'messages.json')
            with open(messages_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            print(f"Error saving message: {e}")
            
        flash("Message sent successfully! ", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/tutorials')
def tutorials(): return render_template('construction.html')

@app.route('/about')
def about(): return render_template('construction.html')

@app.route('/api/generate-art', methods=['POST'])
def api_generate_art():
    try:
        data = request.json
        art_type = data.get('type')
        num_shapes = data.get('num_shapes', 150)
        bg_color = data.get('bg_color', '#1a1a1a')
        
        # Initialiser le générateur
        generator = StudioArtGenerator(app.config['OUTPUT_FOLDER'])
        filename = ""
        
        # Déterminer quel art générer
        if art_type == 'oop':
            filename = generator.generate_oop_chaos(num_shapes=num_shapes, bg_color=bg_color)
        elif art_type == 'fractal':
            filename = generator.generate_fractal_tree(bg_color=bg_color)
        elif art_type == 'grid':
            filename = generator.generate_dynamic_grid(bg_color=bg_color)
        else:
            return jsonify({"status": "error", "message": "Type d'art invalide"}), 400
            
        # Renvoyer l'URL exacte attendue par le JavaScript
        image_url = f"/{app.config['OUTPUT_FOLDER']}/{filename}"
        
        return jsonify({
            "status": "success",
            "image_url": image_url
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'assets_metadata.csv')
    app.run(host='0.0.0.0', port=5000, debug=True, extra_files=[csv_path]) #app.run(host='0.0.0.0', port=5000, debug=True, extra_files=[csv_path])    
