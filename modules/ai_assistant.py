import os
import random

class ArtAssistant:
    def __init__(self, output_folder):
        self.output_folder = output_folder

    def analyze_gallery(self):
        """Kay-scaner dossier bach y3tina stats"""
        if not os.path.exists(self.output_folder):
            return {"total": 0, "drawings": 0, "charts": 0, "edited": 0}

        files = os.listdir(self.output_folder)
        drawings = len([f for f in files if f.startswith('drawing_')])
        charts = len([f for f in files if f.startswith('chart_') or f.startswith('data_')])
        edited = len([f for f in files if f.startswith('edited_')])
        
        return {
            "total": len(files),
            "drawings": drawings,
            "charts": charts,
            "edited": edited
        }

    def get_response(self, user_message):
        """Hna fin kayn l'Logic (Brain)"""
        msg = user_message.lower()
        stats = self.analyze_gallery()
        
        # 1. Personalisation sur la Data (Stats)
        if "how many" in msg or "count" in msg or "stats" in msg or "ch7al" in msg:
            return (f"📊 Analysis of your Studio:\n"
                    f"- Total Artworks: {stats['total']}\n"
                    f"- Drawings: {stats['drawings']}\n"
                    f"- Data Charts: {stats['charts']}\n"
                    f"- Edited Photos: {stats['edited']}\n"
                    f"You are being very productive! 🎨")

        # 2. Guidance (Tawjih)
        elif "draw" in msg or "paint" in msg or "rsm" in msg:
            return "To start drawing, go to 'Studio Paint' (Generative Art). You can use brushes, shapes, and save your work! 🎨"
        
        elif "data" in msg or "chart" in msg or "csv" in msg:
            return "Head over to 'Data Visualization'. Upload a CSV file and I will help you turn it into a Bar, Line, or Donut chart! 📈"

        elif "photo" in msg or "filter" in msg or "image" in msg:
            return "Use 'Media Tools' to apply artistic filters like Grayscale, Blur, or Edge Detection to your photos. 📸"

        # 3. Small Talk (Chat)
        elif "hello" in msg or "hi" in msg or "salam" in msg:
            return "Hello! I am your Creative AI Assistant. How can I help you create art today? 🤖"

        elif "who are you" in msg:
            return "I am the Neural Core of this Interactive Studio. I monitor your gallery and guide your creativity."

        else:
            return "I'm focusing on your art right now. Ask me about your Gallery, Drawing tools, or Data visualization! 🤔"