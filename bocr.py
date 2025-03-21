import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

def select_image():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Imágenes", "*.jpg;*.png;*.jpeg;*.png")]
    )

def detect_braille_dots(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dots = [
        cv2.boundingRect(cnt) for cnt in contours if cv2.contourArea(cnt) > 10
    ]
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

    # Dibujar divisiones horizontales (3 filas)
    total_height = y_max - y_min
    section_height = total_height // 3
    for i in range(3):
        y1 = y_min + i * section_height
        y2 = y1 + section_height
        cv2.rectangle(output, (x_min, y1), (x_max, y2), (255, 0, 0), 1)

    # Dibujar líneas amarillas (bordes de puntos)
    line_positions = []
    for (x, y, w, h) in dots:
        left = x
        right = x + w
        line_positions.append(left)
        line_positions.append(right)
        cv2.line(output, (left, y_min), (left, y_max), (0, 255, 255), 1)
        cv2.line(output, (right, y_min), (right, y_max), (0, 255, 255), 1)

    # Ordenar líneas amarillas
    line_positions = sorted(set(line_positions))

    # Detectar bloques verdes y guardar sus bordes
    green_blocks = []
    green_lines = []  # aquí guardamos líneas verdes para medir distancias luego

    for i in range(0, len(line_positions) - 3, 4):
        x1 = line_positions[i]
        x4 = line_positions[i + 3]
        green_blocks.append((x1, x4))
        green_lines.append(x1)
        green_lines.append(x4)
        cv2.rectangle(output, (x1, y_min), (x4, y_max), (0, 255, 0), 2)

    if len(green_lines) < 2:
        print("No hay suficientes líneas verdes para calcular interlineado.")
        return output

    # Ordenar líneas verdes y calcular la distancia mínima
    green_lines = sorted(set(green_lines))
    interlineado = float("inf")
    for i in range(1, len(green_lines)):
        dist = green_lines[i] - green_lines[i - 1]
        if 0 < dist < interlineado:
            interlineado = dist

    # Calcular ancho promedio de los bloques verdes
    green_widths = [x4 - x1 for (x1, x4) in green_blocks]
    if not green_widths:
        print("No se pudo calcular ancho de bloques verdes.")
        return output
    ancho_bloque_verde = int(np.median(green_widths))  # usamos mediana para evitar outliers

    # Buscar bloque verde que toque el borde derecho
    selected_block = None
    for (x1, x4) in green_blocks:
        if abs(x4 - x_max) <= 3:  # tolerancia
            selected_block = (x1, x4)
            break

    if not selected_block:
        print("No se encontró bloque verde tocando el borde derecho.")
        return output


    return output

def main():
    image_path = select_image()
    if not image_path:
        print("No se seleccionó ninguna imagen.")
        return

    dots, image = detect_braille_dots(image_path)
    result = draw_grid_from_dots(image, dots)

    cv2.imshow("Braille - Morados con espacio de bloque verde", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
