import fitz  # PyMuPDF
import cv2
import numpy as np

class Point:
    def __init__(self, x, y, color):
        self.x = x  # X-Koordinate (in mm)
        self.y = y  # Y-Koordinate (in mm)
        self.color = color  # Farbe (RGB)
        self.attributes = {}  # Zusätzliche Attribute

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def get_attribute(self, key):
        return self.attributes.get(key, None)

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, color={self.color}, attributes={self.attributes})"

class MapProcessor:
    def __init__(self, image_path, map_width, map_height, grid_size):
        self.image_path = image_path
        self.map_width = map_width  # Breite der Karte in mm
        self.map_height = map_height  # Höhe der Karte in mm
        self.grid_size = grid_size  # Abstand zwischen den Punkten im Raster (in Pixeln)
        self.points = []  # Liste von Point-Objekten

    def process_map(self):
        # Lade das Bild
        image = cv2.imread(self.image_path)
        if image is None:
            raise FileNotFoundError(f"Bild konnte nicht geladen werden: {self.image_path}")
        
        # Bildgröße in Pixeln
        img_height, img_width, _ = image.shape

        # Berechne das Verhältnis zwischen Bildpixeln und realen Einheiten (mm)
        x_ratio = 2350 / img_width  # Breite der Karte in mm (235 cm)
        y_ratio = 1150 / img_height  # Höhe der Karte in mm (115 cm)

        # Rasterisiere die Karte
        for y in range(0, img_height, self.grid_size):
            for x in range(0, img_width, self.grid_size):
                # Runde die Pixelkoordinaten
                rounded_x = round(x)
                rounded_y = round(y)

                # Hole die Farbe des Pixels
                b, g, r = image[rounded_y, rounded_x]
                color = (r, g, b)  # Farbe im RGB-Format

                # Berechne die realen Koordinaten in mm
                real_x = rounded_x * x_ratio
                real_y = rounded_y * y_ratio

                # Erstelle ein Point-Objekt und füge es zur Liste hinzu
                point = Point(real_x, real_y, color)
                self.points.append(point)

    def get_points_by_color(self, target_color):
        # Finde alle Punkte mit der angegebenen Farbe
        return [point for point in self.points if point.color == target_color]

    def get_point_by_coordinate(self, x, y):
        # Hole den Punkt für eine bestimmte Koordinate
        for point in self.points:
            if point.x == x and point.y == y:
                return point
        return None

# Funktion zum Rendern der PDF-Seite als Bild
def render_pdf_to_image(pdf_path, output_image_path, dpi=300):
    """
    Rendert die erste Seite einer PDF-Datei als Bild und speichert sie.
    """
    doc = fitz.open(pdf_path)
    page = doc[0]  # Nimm die erste Seite
    pix = page.get_pixmap(dpi=dpi)  # Render die Seite mit der angegebenen DPI
    pix.save(output_image_path)  # Speichere das Bild
    print(f"Seite als Bild gespeichert: {output_image_path}")
    doc.close()

def crop_white_border(image, threshold=240):
    """
    Entfernt den weißen Rand eines Bildes basierend auf einem Helligkeitsschwellenwert.
    :param image: Eingabebild (als NumPy-Array)
    :param threshold: Helligkeitsschwellenwert (0-255)
    :return: Beschnittenes Bild
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Konvertiere zu Graustufen
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)  # Invertiere Farben
    coords = cv2.findNonZero(binary)  # Finde nicht-weiße Pixel
    x, y, w, h = cv2.boundingRect(coords)  # Berechne das begrenzende Rechteck
    cropped_image = image[y:y+h, x:x+w]  # Schneide das Bild zu
    return cropped_image

# Beispielaufruf
pdf_path = r".\ressources\map.pdf"
output_image_path = r".\ressources\map.png"
render_pdf_to_image(pdf_path, output_image_path, dpi=300)

# Verarbeite die Karte
map_width = 2350  # Breite der Karte in mm (235 cm)
map_height = 1150  # Höhe der Karte in mm (115 cm)

# Dynamische Berechnung des grid_size basierend auf der kurzen Seite
desired_points_short_side = 200  # Gewünschte Anzahl von Punkten auf der kurzen Seite
image = cv2.imread(output_image_path)
if image is None:
    raise FileNotFoundError("Das Bild konnte nicht geladen werden.")

# Entferne den weißen Rand
image = crop_white_border(image)

# Aktualisiere die Bildgröße nach dem Zuschneiden
img_height, img_width, _ = image.shape
grid_size = max(1, img_height // desired_points_short_side)  # Rastergröße in Pixeln

processor = MapProcessor(output_image_path, map_width, map_height, grid_size)
processor.process_map()

# Debugging: Überprüfe die Bildgröße und Rastergröße
print(f"Bildgröße nach Zuschneiden: Breite={img_width}, Höhe={img_height}")
print(f"Berechneter grid_size: {grid_size}")

# Debugging: Begrenze die Ausgabe der Rasterisierung
for y in range(0, img_height, grid_size):
    for x in range(0, img_width, grid_size):
        b, g, r = image[y, x]
        color = (r, g, b)
        if x % 100 == 0 and y % 100 == 0:  # Nur jeden 100. Pixel ausgeben
            print(f"Pixel bei ({x}, {y}): Farbe {color}")

# Debugging: Überprüfe die Schleifenlogik
for y in range(0, img_height, grid_size):
    for x in range(0, img_width, grid_size):
        if x >= img_width or y >= img_height:
            print(f"Fehler: Schleifenkoordinaten außerhalb der Bildgrenzen ({x}, {y})")

# Debugging: Überprüfe die Farbabfrage mit Toleranz
def get_points_by_color_with_tolerance(points, target_color, tolerance=10):
    def is_within_tolerance(color1, color2, tolerance):
        return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

    return [point for point in points if is_within_tolerance(point.color, target_color, tolerance)]

# Beispiel: Abfrage aller Punkte mit einer bestimmten Farbe und Toleranz
target_color = (255, 0, 0)  # Rot
tolerance = 10
rote_punkte = get_points_by_color_with_tolerance(processor.points, target_color, tolerance)
print("Punkte mit der Farbe Rot (mit Toleranz):", rote_punkte)

# Beispiel: Abfrage eines Punktes an einer bestimmten Koordinate
x, y = 50, 50  # Koordinaten in mm
punkt = processor.get_point_by_coordinate(x, y)
if punkt:
    print(f"Punkt an Koordinate ({x}, {y}):", punkt)
else:
    print(f"Kein Punkt an Koordinate ({x}, {y}) gefunden.")

# Speichere die Punkte in einer Datei
output_data_path = r".\ressources\points_data.txt"
with open(output_data_path, "w") as file:
    for point in processor.points:
        file.write(f"{point}\n")
print(f"Punkte wurden in {output_data_path} gespeichert.")