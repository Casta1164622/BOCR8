import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog

# Diccionario de conversión de puntos Braille a caracteres Unicode
braille_dict = {
    (0,0
    ,0,0
    ,0,0): "⠀",

    (1,0
    ,0,0
    ,0,0): "⠁",

    (1,0
    ,1,0
    ,0,0): "⠃",

    (1,1
    ,0,0
    ,0,0): "⠉",

    (1,1
    ,0,1
    ,0,0): "⠙",

    (1,0
    ,0,1
    ,0,0): "⠑",

    (1,1
    ,1,0
    ,0,0): "⠋",

    (1,1
    ,1,1
    ,0,0): "⠛",

    (1,0
    ,1,1
    ,0,0): "⠓",

    (0,1
    ,1,0
    ,0,0): "⠊",

    (0,1
    ,1,1
    ,0,0): "⠚",

    (0,1
    ,0,0
    ,0,0): "⠈",

    (0,1
    ,0,1
    ,0,0): "⠘",

    (0,0
    ,0,0
    ,1,0): "⠄",

    (1,0
    ,0,0
    ,1,0): "⠅",

    (1,0
    ,1,0
    ,1,0): "⠇",

    (1,1
    ,0,0
    ,1,0): "⠍",

    (1,1
    ,0,1
    ,1,0): "⠝",

    (1,0
    ,0,1
    ,1,0): "⠕",
    
    (1,1
    ,1,0
    ,1,0): "⠏",

    (1,1
    ,1,1
    ,1,0): "⠟",

    (1,0
    ,1,1
    ,1,0): "⠗",

    (0,1
    ,1,0
    ,1,0): "⠎",

    (0,1
    ,1,1
    ,1,0): "⠞",

    (0,1
    ,0,0
    ,1,0): "⠌",

    (0,1
    ,0,1
    ,1,0): "⠜",
    
    (0,0
    ,0,0
    ,1,1): "⠤",
    
    (1,0
    ,0,0
    ,1,1): "⠥",

    (1,0
    ,1,0
    ,1,1): "⠧",

    (1,1
    ,0,0
    ,1,1): "⠭",

    (1,1
    ,0,1
    ,1,1): "⠽",

    (1,0
    ,0,1
    ,1,1): "⠵",

    (1,1
    ,1,0
    ,1,1): "⠯",

    (1,1
    ,1,1
    ,1,1): "⠿",

    (1,0
    ,1,1
    ,1,1): "⠷",
    
    (0,1
    ,1,0
    ,1,1): "⠮",
    
    (0,1
    ,1,1
    ,1,1): "⠾",

    (0,1
    ,0,0
    ,1,1): "⠬",

    (0,1
    ,0,1
    ,1,1): "⠼",

    (0,0
    ,0,0
    ,0,1): "⠠",

    (1,0
    ,0,0
    ,0,1): "⠡",

    (1,0
    ,1,0
    ,0,1): "⠣",

    (1,1
    ,0,0
    ,0,1): "⠩",

    (1,1
    ,0,1
    ,0,1): "⠹",
    
    (1,0
    ,0,1
    ,0,1): "⠱",
    
    (1,1
    ,1,0
    ,0,1): "⠫",

    (1,1
    ,1,1
    ,0,1): "⠻",

    (1,0
    ,1,1
    ,0,1): "⠳",

    (0,1
    ,1,0
    ,0,1): "⠪",

    (0,1
    ,1,1
    ,0,1): "⠺",

    (0,1
    ,0,0
    ,0,1): "⠨",

    (0,1
    ,0,1
    ,0,1): "⠸",

    (0,0
    ,1,0
    ,0,0): "⠂",
    
    (0,0
    ,1,0
    ,1,0): "⠆",
    
    (0,0
    ,1,1
    ,0,0): "⠒",

    (0,0
    ,1,1
    ,0,1): "⠲",

    (0,0
    ,1,0
    ,0,1): "⠢",

    (0,0
    ,1,1
    ,1,0): "⠖",

    (0,0
    ,1,1
    ,1,1): "⠶",

    (0,0
    ,1,0
    ,1,1): "⠦",

    (0,0
    ,0,1
    ,1,0): "⠔",

    (0,0
    ,0,1
    ,1,1): "⠴",
    
    (0,0
    ,0,1
    ,0,0): "⠐",
    
    (0,0
    ,0,1
    ,0,1): "⠰",   
}

# Función para seleccionar una imagen desde el explorador
def seleccionar_imagen():
    root = tk.Tk()
    root.withdraw()
    ruta_imagen = filedialog.askopenfilename(title="Selecciona una imagen", filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp")])
    return ruta_imagen

# Función principal para detectar puntos de Braille y convertirlos en texto
def detectar_puntos_braille_con_cuadricula(ruta_imagen):
    if not ruta_imagen:
        print("No se seleccionó ninguna imagen.")
        return

    # Cargar imagen en escala de grises
    imagen = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)

    # Aplicar preprocesamiento (suavizado y binarización)
    imagen_suavizada = cv2.GaussianBlur(imagen, (5, 5), 0)
    _, imagen_binaria = cv2.threshold(imagen_suavizada, 100, 255, cv2.THRESH_BINARY_INV)

    # Detectar contornos
    contornos, _ = cv2.findContours(imagen_binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Crear imagen en color para visualizar los puntos detectados
    imagen_color = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)

    # Filtrar puntos de Braille
    puntos = []
    for contorno in contornos:
        x, y, w, h = cv2.boundingRect(contorno)
        if 3 < w < 25 and 3 < h < 25:  # Ajuste más fino para evitar detectar ruido
            puntos.append((x, y))
            cv2.rectangle(imagen_color, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Dibujar los puntos detectados

    if not puntos:
        print("No se detectaron puntos de Braille.")
        return

    # Ordenar los puntos por filas y columnas
    puntos.sort(key=lambda p: (p[1], p[0]))  # Ordenar por Y (filas) y luego por X (columnas)

    # Calcular el espacio promedio entre caracteres Braille
    espacios_x = []
    for i in range(1, len(puntos)):
        espacio = puntos[i][0] - puntos[i - 1][0]
        if espacio > 5:  # Evitar detectar ruido como separación
            espacios_x.append(espacio)

    if espacios_x:
        espacio_medio_x = int(np.median(espacios_x))  # Usar la mediana para evitar valores atípicos
    else:
        espacio_medio_x = 25  # Valor por defecto si no se detecta un buen patrón

    # Calcular los límites de la cuadrícula
    min_x = min(p[0] for p in puntos)
    max_x = max(p[0] for p in puntos)
    min_y = min(p[1] for p in puntos)
    max_y = max(p[1] for p in puntos)

    ancho_celda = espacio_medio_x  # Separación entre caracteres Braille
    alto_celda = 30  # Altura estándar de una celda de Braille

    # Dibujar cuadrícula sobre la imagen
    for x in range(min_x, max_x + ancho_celda, ancho_celda):
        cv2.line(imagen_color, (x, min_y), (x, max_y), (255, 0, 0), 1)

    for y in range(min_y, max_y + alto_celda, alto_celda):
        cv2.line(imagen_color, (min_x, y), (max_x, y), (255, 0, 0), 1)

    # **Detectar caracteres Braille**
    texto_braille = ""
    for x in range(min_x, max_x, ancho_celda):  # Recorrer columnas
        for y in range(min_y, max_y, alto_celda):  # Recorrer filas
            celda = [0] * 6
            for i, (px, py) in enumerate(puntos):
                if x <= px < x + ancho_celda and y <= py < y + alto_celda:
                    if y <= py < y + alto_celda / 3:  # Primera fila (puntos 1 y 4)
                        celda[0 if px < x + ancho_celda / 2 else 3] = 1
                    elif y + alto_celda / 3 <= py < y + 2 * alto_celda / 3:  # Segunda fila (puntos 2 y 5)
                        celda[1 if px < x + ancho_celda / 2 else 4] = 1
                    else:  # Tercera fila (puntos 3 y 6)
                        celda[2 if px < x + ancho_celda / 2 else 5] = 1

            # Convertir celda a caracter Braille
            texto_braille += braille_dict.get(tuple(celda), "?")  # "?" si no está en el diccionario

        texto_braille += " "  # Espaciado entre caracteres

    print("Texto en Braille detectado:", texto_braille)

    # Mostrar la imagen con la cuadrícula corregida
    cv2.imshow("Puntos de Braille con Cuadrícula Ajustada", imagen_color)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# **Ejemplo de uso**
imagen_seleccionada = seleccionar_imagen()
detectar_puntos_braille_con_cuadricula(imagen_seleccionada)
