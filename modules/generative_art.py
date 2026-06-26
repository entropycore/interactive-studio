import matplotlib
matplotlib.use('Agg') # Muhim bzaf bach Flask may plantéch
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
import os
import uuid
import math

# --- OOP REQUIREMENTS ---
class Shape:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, ax):
        pass

class Circle(Shape):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, color)
        self.radius = radius

    def draw(self, ax):
        circle = patches.Circle((self.x, self.y), self.radius, facecolor=self.color, alpha=0.6, edgecolor='white', linewidth=1)
        ax.add_patch(circle)

class Square(Shape):
    def __init__(self, x, y, size, color):
        super().__init__(x, y, color)
        self.size = size

    def draw(self, ax):
        rect = patches.Rectangle((self.x, self.y), self.size, self.size, facecolor=self.color, alpha=0.6, edgecolor='white', linewidth=1)
        ax.add_patch(rect)

# --- GENERATOR CLASS ---
class StudioArtGenerator:
    def __init__(self, output_folder="static/outputs"):
        self.output_folder = output_folder
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def _get_random_hex_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def _setup_plot(self, bg_color):
        fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
        ax.set_facecolor(bg_color)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        return fig, ax

    def _save_and_close(self, fig, prefix):
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(self.output_folder, filename)
        plt.savefig(filepath, format='png', bbox_inches='tight', pad_inches=0, facecolor=fig.get_facecolor())
        plt.close(fig)
        return filename

    # Artwork 1: OOP Geometric
    def generate_oop_chaos(self, num_shapes=150, bg_color='#1a1a1a'):
        fig, ax = self._setup_plot(bg_color) # On utilise la couleur dynamique
        shapes = []
        for _ in range(num_shapes): # On utilise le nombre dynamique
            x, y = random.uniform(0, 100), random.uniform(0, 100)
            color = self._get_random_hex_color()
            if random.choice([True, False]):
                shapes.append(Circle(x, y, random.uniform(2, 12), color))
            else:
                shapes.append(Square(x, y, random.uniform(4, 15), color))
                
        for shape in shapes:
            shape.draw(ax)
        return self._save_and_close(fig, "oop_art")

    # Artwork 2: Fractal Tree
    def generate_fractal_tree(self, bg_color='#2c3e50'):
        fig, ax = self._setup_plot(bg_color) # On utilise la couleur dynamique
        
        def draw_branch(x, y, angle, length, depth):
            if depth == 0:
                return
            x2 = x + math.cos(math.radians(angle)) * length
            y2 = y + math.sin(math.radians(angle)) * length
            
            thickness = max(1, depth * 0.5)
            ax.plot([x, x2], [y, y2], color='#e74c3c', linewidth=thickness, alpha=0.8)
            
            new_length = length * random.uniform(0.6, 0.8)
            draw_branch(x2, y2, angle - random.randint(15, 30), new_length, depth - 1)
            draw_branch(x2, y2, angle + random.randint(15, 30), new_length, depth - 1)

        draw_branch(50, 0, 90, 25, 8)
        return self._save_and_close(fig, "fractal_art")

    # Artwork 3: Dynamic Grid
    def generate_dynamic_grid(self, bg_color='#ecf0f1'):
        fig, ax = self._setup_plot(bg_color) # On utilise la couleur dynamique
        step = 10
        for x in range(0, 100, step):
            for y in range(0, 100, step):
                if random.random() > 0.3:
                    color = self._get_random_hex_color()
                    if random.random() > 0.5:
                        circle = patches.Circle((x+step/2, y+step/2), step/2.5, facecolor=color)
                        ax.add_patch(circle)
                    else:
                        ax.plot([x, x+step], [y, y+step], color=color, linewidth=3)
                        ax.plot([x+step, x], [y, y+step], color=color, linewidth=3)
        return self._save_and_close(fig, "grid_art")