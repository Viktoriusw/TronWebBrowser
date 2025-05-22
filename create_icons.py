from PIL import Image, ImageDraw
import os
from math import cos, sin, radians

def create_icon(name, color, size=(32, 32)):
    # Crear una imagen con fondo transparente
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Dibujar el icono según el nombre
    if name == 'back':
        # Flecha hacia la izquierda
        points = [(24, 4), (8, 16), (24, 28)]
        draw.polygon(points, fill=color)
    elif name == 'forward':
        # Flecha hacia la derecha
        points = [(8, 4), (24, 16), (8, 28)]
        draw.polygon(points, fill=color)
    elif name == 'refresh':
        # Círculo con flecha
        draw.arc([4, 4, 28, 28], 0, 360, fill=color, width=2)
        points = [(20, 8), (28, 16), (20, 24)]
        draw.polygon(points, fill=color)
    elif name == 'new-tab':
        # Página con + en la esquina
        draw.rectangle([4, 4, 28, 28], outline=color, width=2)
        draw.line([20, 12, 20, 20], fill=color, width=2)
        draw.line([16, 16, 24, 16], fill=color, width=2)
    elif name == 'bookmark':
        # Marcador
        points = [(4, 4), (16, 16), (28, 4), (28, 28), (4, 28)]
        draw.polygon(points, fill=color)
    elif name == 'history':
        # Reloj
        draw.ellipse([4, 4, 28, 28], outline=color, width=2)
        draw.line([16, 16, 16, 8], fill=color, width=2)
        draw.line([16, 16, 22, 16], fill=color, width=2)
    elif name == 'settings':
        # Engranaje
        draw.ellipse([8, 8, 24, 24], outline=color, width=2)
        draw.ellipse([14, 14, 18, 18], fill=color)
        for i in range(8):
            angle = i * 45
            x1 = 16 + 12 * cos(radians(angle))
            y1 = 16 + 12 * sin(radians(angle))
            x2 = 16 + 16 * cos(radians(angle))
            y2 = 16 + 16 * sin(radians(angle))
            draw.line([x1, y1, x2, y2], fill=color, width=2)
    elif name == 'wrench':
        # Llave inglesa
        draw.rectangle([10, 6, 22, 26], fill=color)
        draw.pieslice([6, 4, 18, 16], 30, 150, fill=color)
    elif name == 'key':
        # Llave
        draw.ellipse([6, 12, 18, 24], outline=color, width=3)
        draw.rectangle([18, 16, 28, 20], fill=color)
        draw.rectangle([24, 14, 28, 16], fill=color)
    elif name == 'lock':
        # Candado
        draw.rectangle([8, 16, 24, 28], fill=color)
        draw.arc([8, 6, 24, 22], 0, 180, fill=color, width=3)
    elif name == 'heart':
        # Corazón
        draw.pieslice([6, 8, 16, 18], 180, 360, fill=color)
        draw.pieslice([16, 8, 26, 18], 180, 360, fill=color)
        draw.polygon([(6, 14), (16, 28), (26, 14)], fill=color)
    
    # Guardar el icono
    if not os.path.exists('icons'):
        os.makedirs('icons')
    img.save(f'icons/{name}.png')

# Crear los iconos
icons = ['back', 'forward', 'refresh', 'new-tab', 'bookmark', 'history', 'settings', 'wrench', 'key', 'lock', 'heart']
for icon in icons:
    create_icon(icon, (0, 0, 0))  # Color negro para los iconos 