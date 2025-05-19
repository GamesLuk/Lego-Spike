import fitz  # PyMuPDF
import cv2 
import csv # CSV

class Point:
    def __init__(self, x, y, color, object):
        self.x = x  # X-Koordinate
        self.y = y  # Y-Koordinate
        self.color = color  # Farbe (RGB)
        self.object = object  # Flag, ob Objekt-Region
        self.attributes = {}  # Zusätzliche Attribute als Dictionary

    def set_attribute(self, key, value): # Attribut setzen
        self.attributes[key] = value

    def get_attribute(self, key):   # Attribut abfragen
        return self.attributes.get(key, None) 

    def __repr__(self): # String-Repräsentation des Punktes
        return f"Point(x={self.x}, y={self.y}, color={self.color}, attributes={self.attributes})"
    
#----------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------#

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

    def save_points_to_csv(self, output_path):  # Speichere die Punkte in einer CSV-Datei
        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["x", "y", "r", "g", "b", "object"])  # Header
            for point in self.points:
                r, g, b = point.color
                writer.writerow([point.x, point.y, r, g, b, point.object, point.attributes])  # Schreibe die Punktdaten

#----------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------#

# Funktion zum Rendern der PDF-Seite als Bild
def render_pdf_to_image(pdf_path, output_image_path, dpi=300):
    doc = fitz.open(pdf_path)
    page = doc[0]  # Nimm die erste Seite
    pix = page.get_pixmap(dpi=dpi)  # Render die Seite mit der angegebenen DPI
    pix.save(output_image_path)  # Speichere das Bild
    print(f"Seite als Bild gespeichert: {output_image_path}")
    doc.close()

def crop_white_border(image, threshold=240):    # Funktion zum Zuschneiden des weißen Randes
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Konvertiere zu Graustufen
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)  # Invertiere Farben
    coords = cv2.findNonZero(binary)  # Finde nicht-weiße Pixel
    x, y, w, h = cv2.boundingRect(coords)  # Berechne das begrenzende Rechteck
    cropped_image = image[y:y+h, x:x+w]  # Schneide das Bild zu
    cv2.imwrite(r".\ressources\cropped_map.png", cropped_image)  # Speichere das zugeschnittene Bild
    return cropped_image

#----------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------#

# Vars
pdf_path = r".\ressources\map.pdf"
output_image_path = r".\ressources\map.png"

# Extrahieren
render_pdf_to_image(pdf_path, output_image_path, dpi=300)

# Debug
image = cv2.imread(output_image_path)
if image is None:
    raise FileNotFoundError("Das Bild konnte nicht geladen werden.")

# Entferne den weißen Rand
image = crop_white_border(image)

"""
# Aktualisiere die Bildgröße nach dem Zuschneiden
img_height, img_width, _ = image.shape

processor = MapProcessor(output_image_path, grid_size)  # Map-Größe in cm
processor.process_map()

# Speichere die Punkte in einer CSV-Datei
output_data_path = r".\ressources\points_data.csv"
processor.save_points_to_csv(output_data_path)
print(f"Punkte wurden in {output_data_path} gespeichert.")

"""