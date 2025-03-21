import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from collections import Counter

def select_image():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Selecciona una imagen", filetypes=[("Archivos de imagen", "*.jpg;*.png;*.jpeg")])

def detect_braille_dots(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    dots = [cv2.boundingRect(cnt) for cnt in contours if cv2.contourArea(cnt) > 10]
    dots.sort(key=lambda b: (b[1], b[0]))  # Ordenar primero por Y, luego por X
    return dots, image

def calcular_interlineado(dots, y_min, y_max):
    filas = [[] for _ in range(3)]
    altura_total = y_max - y_min
    altura_fila = altura_total / 3

    for x, y, w, h in dots:
        centro_y = y + h // 2
        fila_idx = int((centro_y - y_min) / altura_fila)
        if 0 <= fila_idx < 3:
            centro_x = x + w // 2
            filas[fila_idx].append(centro_x)

    distancias = []
    for fila in filas:
        fila.sort()
        for i in range(1, len(fila)):
            distancias.append(fila[i] - fila[i - 1])

    if not distancias:
        return None

    redondeadas = [round(d / 5) * 5 for d in distancias]
    moda = Counter(redondeadas).most_common(1)[0][0]
    return moda

def draw_grid(image, dots):
    output = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Agrupar en celdas 2x3
    cells = []
    for i in range(0, len(dots), 6):
        group = dots[i:i+6]
        if len(group) == 6:
            x_min = min(dot[0] for dot in group)
            y_min = min(dot[1] for dot in group)
            x_max = max(dot[0] + dot[2] for dot in group)
            y_max = max(dot[1] + dot[3] for dot in group)
            cells.append((x_min, y_min, x_max, y_max))

    if not cells:
        return output

    x1_all = min(cell[0] for cell in cells)
    y1_all = min(cell[1] for cell in cells)
    x2_all = max(cell[2] for cell in cells)
    y2_all = max(cell[3] for cell in cells)

    # Dibujar rectángulo global
    cv2.rectangle(output, (x1_all, y1_all), (x2_all, y2_all), (0, 0, 255), 3)

    # Altura de cuadrito
    cell_height = (y2_all - y1_all) // 3
    interlineado = calcular_interlineado(dots, y1_all, y2_all)
    if not interlineado:
        print("No se pudo calcular interlineado.")
        return output

    # Iniciar desde el borde izquierdo
    x = x1_all
    y_positions = [y1_all + i * cell_height for i in range(3)]

    while x + cell_height <= x2_all:
        # 1. Cuadro de agrupación (cuadrado)
        for y in y_positions:
            cv2.rectangle(output, (x, y), (x + cell_height, y + cell_height), (0, 165, 255), 2)  # naranja

        x += cell_height

        # 2. Cuadro de interlineado (más angosto)
        if x + interlineado <= x2_all:
            for y in y_positions:
                cv2.rectangle(output, (x, y), (x + interlineado, y + cell_height), (0, 255, 255), 1)  # amarillo
            x += interlineado
        else:
            break  # no hay espacio suficiente para otro interlineado + agrupación

    return output

def main():
    image_path = select_image()
    if not image_path:
        print("No se seleccionó ninguna imagen.")
        return

    dots, image = detect_braille_dots(image_path)
    result = draw_grid(image, dots)
    cv2.imshow('Braille Grid Detection', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
