from flask import Flask, render_template, request, redirect, url_for, jsonify,flash
import os
import uuid
import base64
import json
from datetime import datetime
from werkzeug.utils import secure_filename

# --- IMPORTS MODULES ---
from modules.data_viz import DataAnalyzer 
try:
    from modules.media_tools import MediaProcessor
except ImportError:
    MediaProcessor = None
# Import AI Logic
from modules.ai_assistant import ArtAssistant

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'
app.config['CHATS_FILE'] = 'static/chats.json' # Fichier fin ghanhoto l'hdra
app.secret_key = 'super_secret_key'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# --- HELPERS POUR CHAT (JSON) ---
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

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('home.html')

# --- NEW: ROUTE HONAR (FULL PAGE) ---
@app.route('/honar')
def honar():
    # Afficher la page avec l'historique
    chats = load_chats()
    # Tri par date (Jdid lfo9)
    chats.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return render_template('honar.html', chats=chats)

# --- NEW: API POUR HONAR ---
@app.route('/api/chat/new', methods=['POST'])
def new_chat():
    chats = load_chats()
    chat_id = str(uuid.uuid4())
    new_session = {
        "id": chat_id,
        "title": "New Conversation",
        "timestamp": datetime.now().isoformat(),
        "messages": [{"sender": "bot", "text": "Hello! I am Honar. How can I help you create art today? 🎨"}]
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
    # Nl9aw l'chat li hna fih
    session = next((c for c in chats if c['id'] == chat_id), None)
    
    if session:
        # 1. Zid msg dyal user
        session['messages'].append({"sender": "user", "text": user_msg})
        
        # 2. Update Titre ila kan mazal "New Conversation"
        if session['title'] == "New Conversation":
            session['title'] = user_msg[:20] + "..."
            
        # 3. Jib Jawab mn AI
        bot = ArtAssistant(app.config['OUTPUT_FOLDER'])
        bot_response = bot.get_response(user_msg)
        
        # 4. Zid msg dyal bot
        session['messages'].append({"sender": "bot", "text": bot_response})
        session['timestamp'] = datetime.now().isoformat()
        
        save_chats(chats)
        return jsonify({"response": bot_response})
    
    return jsonify({"error": "Chat not found"}), 404

# --- ROUTES DES AUTRES MODULES (Bhal 9bila) ---
@app.route('/gallery')
def gallery():
    drawings = []
    data_art = []
    edited = []
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        files = os.listdir(app.config['OUTPUT_FOLDER'])
        files.sort(key=lambda x: os.path.getmtime(os.path.join(app.config['OUTPUT_FOLDER'], x)), reverse=True)
        for f in files:
            if f.startswith('drawing_'): drawings.append(f)
            elif f.startswith('chart_') or f.startswith('data_') or f.startswith('wave_'): data_art.append(f)
            elif f.startswith('edited_'): edited.append(f)
    return render_template('gallery.html', drawings=drawings, data_art=data_art, edited=edited)

@app.route('/generative', methods=['GET', 'POST'])
def generative():
    if request.method == 'POST':
        image_data = request.form.get('image_data')
        if image_data:
            image_data = image_data.replace('data:image/png;base64,', '')
            filename = f"drawing_{uuid.uuid4().hex}.png"
            filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
            with open(filepath, "wb") as f: f.write(base64.b64decode(image_data))
            return render_template('generative.html', saved_image=filename)
    return render_template('generative.html')

@app.route('/data-art', methods=['GET', 'POST'])
def data_art():
    columns_info = None
    uploaded_file = None
    chart_image = None
    if request.method == 'POST':
        if 'csv_file' in request.files:
            file = request.files['csv_file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                analyzer = DataAnalyzer(app.config['UPLOAD_FOLDER'])
                info = analyzer.get_csv_columns(filename)
                if info['success']: columns_info = info; uploaded_file = filename
        elif 'chart_type' in request.form:
            filename = request.form.get('uploaded_filename')
            chart_type = request.form.get('chart_type')
            x_col = request.form.get('x_axis')
            y_col = request.form.get('y_axis')
            analyzer = DataAnalyzer(app.config['UPLOAD_FOLDER'])
            chart_image = analyzer.create_custom_chart(filename, chart_type, x_col, y_col, app.config['OUTPUT_FOLDER'])
            columns_info = analyzer.get_csv_columns(filename)
            uploaded_file = filename
    return render_template('data_art.html', columns_info=columns_info, uploaded_file=uploaded_file, chart_image=chart_image)

@app.route('/tools', methods=['GET', 'POST'])
def tools():
    image_filename = None
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filter_type = request.form.get('filter_type')
                if MediaProcessor:
                    processor = MediaProcessor(app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'])
                    image_filename = processor.process_image(filename, filter_type)
    return render_template('tools.html', image_filename=image_filename)

@app.route('/editor', methods=['GET', 'POST'])
def editor():
    note_path = os.path.join(app.config['OUTPUT_FOLDER'], 'my_notes.txt')
    if request.method == 'POST':
        with open(note_path, 'w', encoding='utf-8') as f: f.write(request.form.get('content'))
        return render_template('editor.html', content=request.form.get('content'), saved=True)
    content = ""
    if os.path.exists(note_path):
        with open(note_path, 'r', encoding='utf-8') as f: content = f.read()
    return render_template('editor.html', content=content)

@app.route('/assets')
def assets():
    assets_dir = os.path.join('static', 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    return render_template('assets.html', wallpapers=os.listdir(assets_dir))

# Route l'9dima dyal widget (optionnel)
@app.route('/chat', methods=['POST'])
def chat_widget():
    user_message = request.json.get('message')
    bot = ArtAssistant(app.config['OUTPUT_FOLDER'])
    return jsonify({"response": bot.get_response(user_message)})


# --- SEARCH SYSTEM ---
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
    if not query:
        return jsonify([])
    
  
    results = [
        item for item in SITE_CONTENT 
        if query in item['title'].lower() or query in item['keywords']
    ]

    return jsonify(results[:5])





# --- NEW: ROUTE CONTACT FORM ---
  

# flash messages
app.secret_key = 'super_secret_key' 

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # 2. Backend Logic (Validation)
        if not name or not email:
            flash("Please fill all fields!", "error")
            return redirect(url_for('contact'))
            
        data = {"name": name, "email": email, "message": message}
        with open('messages.json', 'a') as f:
            f.write(json.dumps(data) + "\n")
            
        flash("Message sent successfully! 🚀", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')






@app.route('/tutorials')
def tutorials():
    return render_template('construction.html')

@app.route('/about')
def about():
    return render_template('construction.html')






if __name__ == '__main__':
   
   app.run(debug=True)                  # app.run(host='0.0.0.0', port=5000, debug=True) pour le host snd run in phone in the same network