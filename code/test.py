import csv
import cv2
import numpy as np

def load_points_from_csv(file_path):
    """
    Lädt die Punkte aus einer CSV-Datei und gibt eine Liste von Punkten zurück.
    :param file_path: Pfad zur CSV-Datei mit den Punktdaten.
    :return: Liste von Punkten (x, y, color).
    """
    points = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            x = float(row["x"])
            y = float(row["y"])
            r = int(row["r"])
            g = int(row["g"])
            b = int(row["b"])
            points.append((x, y, (r, g, b)))
    return points

def create_image(points, map_width, map_height, output_path, scale=10):
    """
    Erstellt ein Bild basierend auf den Punktkoordinaten und Farben.
    :param points: Liste von Punkten (x, y, color).
    :param map_width: Breite der Karte in cm.
    :param map_height: Höhe der Karte in cm.
    :param output_path: Pfad, um das generierte Bild zu speichern.
    :param scale: Skalierungsfaktor für die Bildauflösung.
    """
    # Berechne die Bildgröße in Pixeln
    img_width = int(map_width * scale)
    img_height = int(map_height * scale)

    # Erstelle ein leeres weißes Bild
    image = np.ones((img_height, img_width, 3), dtype=np.uint8) * 255

    # Zeichne die Punkte auf das Bild
    for x, y, color in points:
        pixel_x = int(x * scale)
        pixel_y = int(y * scale)
        if 0 <= pixel_x < img_width and 0 <= pixel_y < img_height:
            image[pixel_y, pixel_x] = color  # Setze die Farbe des Pixels

    # Speichere das Bild
    cv2.imwrite(output_path, image)
    print(f"Bild wurde gespeichert: {output_path}")

def create_connected_image(points, map_width, map_height, output_path, scale=10):
    """
    Erstellt ein Bild, bei dem die Punkte miteinander verbunden werden, um durchgängige Farbflächen zu erzeugen.
    :param points: Liste von Punkten (x, y, color).
    :param map_width: Breite der Karte in cm.
    :param map_height: Höhe der Karte in cm.
    :param output_path: Pfad, um das generierte Bild zu speichern.
    :param scale: Skalierungsfaktor für die Bildauflösung.
    """
    # Berechne die Bildgröße in Pixeln
    img_width = int(map_width * scale)
    img_height = int(map_height * scale)

    # Erstelle ein leeres weißes Bild
    image = np.ones((img_height, img_width, 3), dtype=np.uint8) * 255

    # Sortiere die Punkte nach ihrer Position (zuerst nach y, dann nach x)
    points.sort(key=lambda p: (p[1], p[0]))

    # Zeichne die Punkte und verbinde sie
    for i in range(len(points) - 1):
        x1, y1, color1 = points[i]
        x2, y2, color2 = points[i + 1]

        # Konvertiere die Koordinaten in Pixel
        pixel_x1 = int(x1 * scale)
        pixel_y1 = int(y1 * scale)
        pixel_x2 = int(x2 * scale)
        pixel_y2 = int(y2 * scale)

        # Zeichne eine Linie zwischen den Punkten
        cv2.line(image, (pixel_x1, pixel_y1), (pixel_x2, pixel_y2), color1, thickness=1)

    # Speichere das Bild
    cv2.imwrite(output_path, image)
    print(f"Verbundenes Bild wurde gespeichert: {output_path}")

def create_filled_image(points, map_width, map_height, output_path, scale=10):
    """
    Erstellt ein Bild, bei dem die Flächen zwischen den Punkten mit den Farben der umliegenden Pixel gefüllt werden.
    :param points: Liste von Punkten (x, y, color).
    :param map_width: Breite der Karte in cm.
    :param map_height: Höhe der Karte in cm.
    :param output_path: Pfad, um das generierte Bild zu speichern.
    :param scale: Skalierungsfaktor für die Bildauflösung.
    """
    # Berechne die Bildgröße in Pixeln
    img_width = int(map_width * scale)
    img_height = int(map_height * scale)

    # Erstelle ein leeres weißes Bild
    image = np.ones((img_height, img_width, 3), dtype=np.uint8) * 255

    # Zeichne die Punkte auf das Bild
    for x, y, color in points:
        pixel_x = int(x * scale)
        pixel_y = int(y * scale)
        if 0 <= pixel_x < img_width and 0 <= pixel_y < img_height:
            image[pixel_y, pixel_x] = color  # Setze die Farbe des Pixels

    # Fülle die Flächen zwischen den Punkten
    image = cv2.GaussianBlur(image, (5, 5), 0)  # Weichzeichner, um die Farben zu glätten

    # Speichere das Bild
    cv2.imwrite(output_path, image)
    print(f"Gefülltes Bild wurde gespeichert: {output_path}")

# Hauptskript
if __name__ == "__main__":
    # Pfad zur Datei mit den Punktdaten
    points_file = r".\ressources\points_data.csv"

    # Lade die Punkte
    points = load_points_from_csv(points_file)

    # Kartengröße in cm (aus main.py)
    map_width = 235  # Breite der Karte in cm
    map_height = 115  # Höhe der Karte in cm

    # Pfad zum Ausgabebild
    output_image_path = r".\ressources\generated_map.png"

    # Erstelle das Bild
    create_image(points, map_width, map_height, output_image_path, scale=10)

    # Pfad zum Ausgabebild für verbundenes Bild
    connected_image_path = r".\ressources\connected_map.png"

    # Erstelle das verbundene Bild
    create_connected_image(points, map_width, map_height, connected_image_path, scale=10)

    # Pfad zum Ausgabebild für gefülltes Bild
    filled_image_path = r".\ressources\filled_map.png"

    # Erstelle das gefüllte Bild
    create_filled_image(points, map_width, map_height, filled_image_path, scale=10)
