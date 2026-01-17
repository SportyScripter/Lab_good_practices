import os
import glob
import xml.etree.ElementTree as ET

ANNOTATIONS_DIR = "../data/annotations"

files = glob.glob(os.path.join(ANNOTATIONS_DIR, "*.xml"))

if not files:
    print("BŁĄD: Nie znaleziono żadnych plików XML w", ANNOTATIONS_DIR)
else:
    print(f"Znaleziono {len(files)} plików XML.")
    # Sprawdź pierwszy plik
    first_file = files[0]
    print(f"Analizuję plik: {first_file}")
    
    tree = ET.parse(first_file)
    root = tree.getroot()
    
    found_objects = []
    for obj in root.findall('object'):
        name = obj.find('name').text
        found_objects.append(name)
        
    print("Znalezione obiekty (etykiety):", found_objects)