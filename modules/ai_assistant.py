import os
import google.generativeai as genai
from dotenv import load_dotenv
from modules.assets_manager import get_art_wallpapers

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

class ArtAssistant:
    def __init__(self):
      
        self.model_name = 'gemini-2.5-flash' 
        self.model = genai.GenerativeModel(self.model_name)
        
        self.gallery_data = get_art_wallpapers()

    def analyze_user_activity(self):
        self.output_folder = os.path.join('static', 'outputs')
        if not os.path.exists(self.output_folder): return "No activity."
        files = os.listdir(self.output_folder)
        return f"User has created {len(files)} files."

    def get_response(self, user_message):
        if not api_key: return "Error: Check .env"
        
        # Stats Simples
        stats = self.analyze_user_activity()
        
        # Prompt Optimization 
        system_prompt = f"""
        ROLE: You are 'Honar', AI Curator of Gen Studio, and a highly capable, general AI assistant.
        DATA: {str(self.gallery_data)}
        USER STATS: {stats}
        STYLE: Professional, direct, helpful, and concise. 
        FORMATTING RULES: 
        1. Use HTML tags for formatting. 
        2. Use <b> for titles or emphasis. 
        3. Use <br> for line breaks and paragraphs. 
        4. NEVER use markdown symbols like ** or *.
        You MUST answer all user questions clearly and accurately, including general knowledge, history, math, and facts.
        """
        
        try:
            full_prompt = f"{system_prompt}\n\nUSER: {user_message}"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            
            return "Honar is recalibrating... (Use standard model for faster response)."