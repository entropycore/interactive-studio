import random
import os
import uuid
import math
from PIL import Image, ImageDraw

# ==========================================
# 1. COLOR PALETTES (لألوان متناسقة واحترافية)
# ==========================================
PALETTES = {
    "cyberpunk": [(255, 0, 60, 200), (0, 240, 255, 200), (250, 255, 0, 200), (18, 16, 31, 255)],
    "vintage": [(239, 224, 185, 200), (181, 101, 118, 200), (109, 89, 122, 200), (53, 92, 125, 200)],
    "nature": [(45, 106, 79, 200), (64, 145, 108, 200), (116, 198, 157, 200), (216, 243, 220, 200)]
}

# ==========================================
# 2. OOP: BASE CLASS & SUBCLASSES (كيفما طالب الأستاذ)
# ==========================================
class Shape:
    """Base class for all geometric shapes"""
    def __init__(self, x, y, size, color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, draw_obj):
        pass # سيتم تحديدها في الـ Subclasses

class Circle(Shape):
    def draw(self, draw_obj):
        bbox = [self.x, self.y, self.x + self.size, self.y + self.size]
        draw_obj.ellipse(bbox, fill=self.color, outline=(255, 255, 255, 100), width=2)

class Rectangle(Shape):
    def draw(self, draw_obj):
        bbox = [self.x, self.y, self.x + self.size, self.y + self.size]
        draw_obj.rectangle(bbox, fill=self.color, outline=(0, 0, 0, 150), width=2)

class Triangle(Shape):
    def draw(self, draw_obj):
        # حساب رؤوس المثلث
        p1 = (self.x, self.y - self.size)
        p2 = (self.x - self.size, self.y + self.size)
        p3 = (self.x + self.size, self.y + self.size)
        draw_obj.polygon([p1, p2, p3], fill=self.color, outline=(255, 255, 255, 150))

# ==========================================
# 3. GENERATIVE ART STUDIO (المدير الرئيسي)
# ==========================================
class GenerativeArt:
    def __init__(self, width=1000, height=1000, theme="cyberpunk"):
        self.width = width
        self.height = height
        self.theme = theme
        self.palette = PALETTES.get(theme, PALETTES["cyberpunk"])
        
        # استعملنا RGBA باش نقدروا نخدمو بالشفافية (Transparency)
        self.bg_color = (15, 15, 15, 255) if theme == "cyberpunk" else (245, 245, 245, 255)
        self.image = Image.new("RGBA", (width, height), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)

    def get_random_color(self):
        """اختيار لون عشوائي من الباليط المحددة"""
        return random.choice(self.palette)

    # 🎨 STYLE 1: Geometric Chaos
    def generate_geometric_chaos(self, count=100):
        for _ in range(count):
            x = random.randint(-50, self.width)
            y = random.randint(-50, self.height)
            size = random.randint(30, 150)
            color = self.get_random_color()
            
            # اختيار شكل عشوائي (Polymorphism in action)
            shape_type = random.choice([Circle, Rectangle, Triangle])
            shape = shape_type(x, y, size, color)
            shape.draw(self.draw)

    # 🎨 STYLE 2: Abstract Grid (Mondrian Style)
    def generate_abstract_grid(self, grid_size=10):
        step_x = self.width // grid_size
        step_y = self.height // grid_size
        
        for i in range(grid_size):
            for j in range(grid_size):
                if random.random() > 0.3: # 70% chance to draw
                    x = i * step_x
                    y = j * step_y
                    size = random.randint(step_x // 2, step_x)
                    color = self.get_random_color()
                    
                    shape = Rectangle(x, y, size, color)
                    shape.draw(self.draw)
                else:
                    # إضافة دوائر صغيرة في الفراغات
                    cx = i * step_x + step_x // 2
                    cy = j * step_y + step_y // 2
                    self.draw.ellipse([cx-10, cy-10, cx+10, cy+10], fill=self.get_random_color())

    # 🎨 STYLE 3: Fractal Lines / Network
    def generate_network_nodes(self, node_count=50):
        nodes = [(random.randint(50, self.width-50), random.randint(50, self.height-50)) for _ in range(node_count)]
        
        # رسم الخطوط بين العقد المتقاربة
        for i in range(node_count):
            for j in range(i + 1, node_count):
                dist = math.hypot(nodes[i][0] - nodes[j][0], nodes[i][1] - nodes[j][1])
                if dist < 150: # إذا كانت المسافة قريبة
                    color = self.get_random_color()
                    self.draw.line([nodes[i], nodes[j]], fill=color, width=random.randint(1, 4))
        
        # رسم العقد كدوائر
        for nx, ny in nodes:
            Circle(nx - 10, ny - 10, 20, self.get_random_color()).draw(self.draw)

    def save_image(self, output_folder):
        """حفظ اللوحة مع دمج طبقات الشفافية"""
        filename = f"art_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(output_folder, filename)
        
        # دمج RGBA إلى RGB باش يتسجل مزيان
        final_image = Image.new("RGB", self.image.size, (255, 255, 255))
        final_image.paste(self.image, (0, 0), self.image)
        
        final_image.save(filepath, "PNG")
        return filename