import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

def detect_braille_dots(image_path):
    # Cargar la imagen en escala de grises
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # Aplicar un desenfoque para reducir el ruido
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Aplicar umbralización adaptativa para detectar los puntos
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Encontrar contornos de los puntos detectados
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrar contornos por tamaño
    dot_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 10]
    
    return image, dot_contours

def group_braille_dots(dot_contours):
    # Obtener los centros de los puntos
    centers = [cv2.moments(cnt) for cnt in dot_contours]
    centers = [(int(c["m10"] / c["m00"]), int(c["m01"] / c["m00"])) for c in centers if c["m00"] != 0]
    
    # Ordenar por posición Y y luego por X
    centers.sort(key=lambda x: (x[1], x[0]))
    
    # Agrupar en conjuntos de 6 (2x3)
    braille_cells = [centers[i:i + 6] for i in range(0, len(centers), 6)]
    
    return braille_cells, centers

def merge_and_draw_grid(image, braille_cells, centers):
    output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    merged_cells = []
    
    # Unir rectángulos con la misma altura en uno más grande
    for cell in braille_cells:
        if len(cell) == 6:
            x_coords = [p[0] for p in cell]
            y_coords = [p[1] for p in cell]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            merged_cells.append((x_min, y_min, x_max, y_max))
    
    # Agrupar por altura para unirlos horizontalmente
    merged_cells.sort(key=lambda r: (r[1], r[0]))
    combined_rects = []
    
    while merged_cells:
        x_min, y_min, x_max, y_max = merged_cells.pop(0)
        i = 0
        while i < len(merged_cells):
            x2_min, y2_min, x2_max, y2_max = merged_cells[i]
            if y_min == y2_min and y_max == y2_max:  # Misma altura
                x_max = max(x_max, x2_max)  # Unir horizontalmente
                merged_cells.pop(i)
            else:
                i += 1
        combined_rects.append((x_min, y_min, x_max, y_max))
    
    # Dibujar los rectángulos combinados en azul
    for x_min, y_min, x_max, y_max in combined_rects:
        cv2.rectangle(output, (x_min-5, y_min-5), (x_max+5, y_max+5), (255, 0, 0), 2)
    
    # Dibujar un cuadrado rojo que encierra todos los puntos detectados
    if centers:
        all_x = [p[0] for p in centers]
        all_y = [p[1] for p in centers]
        
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        
        cv2.rectangle(output, (x_min-10, y_min-10), (x_max+10, y_max+10), (0, 0, 255), 2)
    
    return output

def select_image():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=[("Imagenes", "*.jpg;*.png;*.jpeg")])
    return file_path

def main():
    image_path = select_image()
    if not image_path:
        print("No se seleccionó ninguna imagen.")
        return
    
    image, dot_contours = detect_braille_dots(image_path)
    braille_cells, centers = group_braille_dots(dot_contours)
    output = merge_and_draw_grid(image, braille_cells, centers)
    
    # Mostrar la imagen con la cuadrícula
    cv2.imshow("Braille Detection", output)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
