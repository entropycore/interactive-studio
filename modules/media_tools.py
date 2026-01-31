from PIL import Image, ImageFilter, ImageOps
import os
import uuid

class MediaProcessor:
    def __init__(self, upload_folder, output_folder):
        self.upload_folder = upload_folder
        self.output_folder = output_folder

    def process_image(self, filename, filter_type):
        """Applique un filtre sur l'image uploadée"""
        
        # 1. Chemin complet de l'image
        input_path = os.path.join(self.upload_folder, filename)
        
        # 2. Ouvrir l'image
        try:
            img = Image.open(input_path)
        except:
            return None # Erreur si ce n'est pas une image

        # 3. Appliquer le filtre choisi
        if filter_type == "grayscale":
            img = ImageOps.grayscale(img)
        
        elif filter_type == "blur":
            img = img.filter(ImageFilter.GaussianBlur(5))
        
        elif filter_type == "contour":
            # Filtre artistique (Contours)
            img = img.filter(ImageFilter.CONTOUR)
            img = ImageOps.invert(img) # Inverser pour avoir un fond blanc
            
        elif filter_type == "invert":
            # Gérer la transparence (Alpha channel) pour éviter les erreurs
            if img.mode == 'RGBA':
                r, g, b, a = img.split()
                rgb = Image.merge('RGB', (r,g,b))
                inverted = ImageOps.invert(rgb)
                r2, g2, b2 = inverted.split()
                img = Image.merge('RGBA', (r2, g2, b2, a))
            else:
                img = ImageOps.invert(img)

        # 4. Sauvegarder le résultat
        output_filename = f"edited_{uuid.uuid4().hex}.png"
        output_path = os.path.join(self.output_folder, output_filename)
        img.save(output_path)
        
        return output_filename