import fitz  # PyMuPDF
import cv2
import numpy as np
import csv

class Point:
    def __init__(self, x, y, color, object):
        self.x = x  # X-Koordinate (in mm)
        self.y = y  # Y-Koordinate (in mm)
        self.color = color  # Farbe (RGB)
        self.object = object  # Flag, ob es sich um ein Objekt handelt
        self.attributes = {}  # Zusätzliche Attribute als Dictionary

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def get_attribute(self, key):
        return self.attributes.get(key, None)

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y}, color={self.color}, attributes={self.attributes})"

class MapProcessor:
    def __init__(self, image_path, grid_size):
        self.image_path = image_path
        self.grid_size = grid_size  # Abstand zwischen den Punkten im Raster (in Pixeln)
        self.points = []  # Liste von Point-Objekten

    def process_map(self):
        # Lade das Bild
        image = cv2.imread(self.image_path)
        if image is None:
            raise FileNotFoundError(f"Bild konnte nicht geladen werden: {self.image_path}")
        
        # Konvertiere das Bild zu RGB, um Farbveränderungen zu vermeiden
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Bildgröße in Pixeln
        img_height, img_width, _ = image.shape

        # Rasterisiere die Karte
        for y in range(0, img_height, self.grid_size):
            for x in range(0, img_width, self.grid_size):
                # Runde die Pixelkoordinaten
                rounded_x = int(round(x, 0) / 34)
                rounded_y = int(round(y, 0) / 34)

                # Hole die Farbe des Pixels
                r, g, b = image[rounded_y, rounded_x]
                color = (r, g, b)  # Speichere die Farbe als Tupel

                # Object = (229, 0, 109)
                if color == (229, 0, 109):
                    object = True
                else:
                    object = False

                # Erstelle ein Point-Objekt
                point = Point(rounded_x, rounded_y, color, object)
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

    def save_points_to_csv(self, output_path):
        """
        Speichert die Punkte in einer CSV-Datei.
        :param output_path: Pfad zur Ausgabedatei.
        """
        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["x", "y", "r", "g", "b", "object"])  # Header
            for point in self.points:
                r, g, b = point.color
                writer.writerow([point.x, point.y, r, g, b, point.object, point.attributes])  # Schreibe die Punktdaten

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

    # Konvertiere das gespeicherte Bild zu RGB, um Farbveränderungen zu vermeiden
    image = cv2.imread(output_image_path)
    if image is not None:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cv2.imwrite(output_image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))  # Speichere es erneut in RGB

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
    cv2.imwrite("cropped_image.png", cropped_image)  # Speichere das zugeschnittene Bild
    return cropped_image

# Beispielaufruf
pdf_path = r".\ressources\map.pdf"
output_image_path = r".\ressources\map.png"
render_pdf_to_image(pdf_path, output_image_path, dpi=300)

# Dynamische Berechnung des grid_size basierend auf der kurzen Seite
desired_points_short_side = 400  # Erhöhe die Anzahl der Punkte auf der kurzen Seite
image = cv2.imread(output_image_path)
if image is None:
    raise FileNotFoundError("Das Bild konnte nicht geladen werden.")

# Entferne den weißen Rand
image = crop_white_border(image) #!

# Aktualisiere die Bildgröße nach dem Zuschneiden
img_height, img_width, _ = image.shape
grid_size = max(1, img_height // desired_points_short_side)  # Rastergröße in Pixeln

processor = MapProcessor(output_image_path, grid_size)  # Map-Größe in cm
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

# Speichere die Punkte in einer CSV-Datei
output_data_path = r".\ressources\points_data.csv"
processor.save_points_to_csv(output_data_path)
print(f"Punkte wurden in {output_data_path} gespeichert.")