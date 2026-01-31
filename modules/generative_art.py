import random
import os
import uuid
from PIL import Image, ImageDraw

# Hada howa Class li mtlob f'page 1 dyal PDF (OOP)
class GenerativeArt:
    def __init__(self, width=800, height=600, background_color="white"):
        self.width = width
        self.height = height
        # Création d'une image vide
        self.image = Image.new("RGB", (width, height), background_color)
        self.draw = ImageDraw.Draw(self.image)

    def generate_random_color(self):
        """Génère une couleur aléatoire"""
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def draw_shapes(self, shape_type, count):
        """Dessine les formes (Cercles, Rectangles...)"""
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(20, 100)
            color = self.generate_random_color()

            if shape_type == "circles":
                # Dessiner un cercle
                self.draw.ellipse([x, y, x + size, y + size], outline=color, width=3)
            
            elif shape_type == "rectangles":
                # Dessiner un rectangle
                self.draw.rectangle([x, y, x + size, y + size], fill=color, outline="black")
            
            elif shape_type == "lines":
                # Dessiner une ligne
                x2 = random.randint(0, self.width)
                y2 = random.randint(0, self.height)
                self.draw.line([x, y, x2, y2], fill=color, width=3)

    def save_image(self, output_folder):
        """Sauvegarde l'image avec un nom unique et retourne le nom"""
        filename = f"art_{uuid.uuid4().hex}.png"
        filepath = os.path.join(output_folder, filename)
        self.image.save(filepath)
        return filename