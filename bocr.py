import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

def select_image():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Selecciona una imagen", filetypes=[("Imágenes", "*.jpg;*.png;*.jpeg;*.png")])

def detect_braille_dots(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dots = [cv2.boundingRect(cnt) for cnt in contours if cv2.contourArea(cnt) > 10]
    return dots, image

def draw_grid_from_dots(image, dots):
    output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if not dots:
        return output

    # Calcular rectángulo global
    x_coords = [x for (x, y, w, h) in dots]
    y_coords = [y for (x, y, w, h) in dots]
    x_max = max(x + w for (x, y, w, h) in dots)
    y_max = max(y + h for (x, y, w, h) in dots)
    x_min = min(x_coords)
    y_min = min(y_coords)

    # Dibujar rectángulo global (rojo)
    cv2.rectangle(output, (x_min, y_min), (x_max, y_max), (0, 0, 255), 3)

    # Dibujar 3 divisiones horizontales (azul)
    total_height = y_max - y_min
    section_height = total_height // 3
    for i in range(3):
        y_start = y_min + i * section_height
        y_end = y_start + section_height
        cv2.rectangle(output, (x_min, y_start), (x_max, y_end), (255, 0, 0), 1)

    # Obtener líneas amarillas (bordes izq y der de cada punto)
    line_positions = []
    for (x, y, w, h) in dots:
        left = x
        right = x + w
        line_positions.append(left)
        line_positions.append(right)
        cv2.line(output, (left, y_min), (left, y_max), (0, 255, 255), 1)
        cv2.line(output, (right, y_min), (right, y_max), (0, 255, 255), 1)

    # Ordenar y quitar duplicados
    line_positions = sorted(set(line_positions))

    # Agrupar en bloques de 4 líneas → cada grupo representa un carácter Braille
    for i in range(0, len(line_positions) - 3, 4):
        x_start = line_positions[i]
        x_end = line_positions[i + 3]
        cv2.rectangle(output, (x_start, y_min), (x_end, y_max), (0, 255, 0), 2)  # verde

    return output

def main():
    image_path = select_image()
    if not image_path:
        print("No se seleccionó ninguna imagen.")
        return

    dots, image = detect_braille_dots(image_path)
    result = draw_grid_from_dots(image, dots)

    cv2.imshow("Braille - Bloques de Caracteres", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
