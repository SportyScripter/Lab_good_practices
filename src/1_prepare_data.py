import os
import shutil
import xml.etree.ElementTree as ET
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# --- KONFIGURACJA ---
RAW_DATA_DIR = "../data"
OUTPUT_DIR = "../datasets"
IMAGES_DIR = os.path.join(RAW_DATA_DIR, "images")
# Ścieżka do pliku XML
XML_FILE = os.path.join(RAW_DATA_DIR, "annotations", "annotations.xml")


def parse_cvat_xml(xml_file):
    """Parsuje jeden duży plik XML z CVAT i zwraca słownik: {nazwa_pliku: [linie_yolo]}"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    data_map = {}

    # Iterujemy po każdym tagu <image>
    for image in root.findall("image"):
        file_name = image.get("name")
        width = float(image.get("width"))
        height = float(image.get("height"))

        yolo_lines = []

        # Szukamy ramek <box> wewnątrz obrazka
        for box in image.findall("box"):
            if box.get("label") == "plate":
                xtl = float(box.get("xtl"))
                ytl = float(box.get("ytl"))
                xbr = float(box.get("xbr"))
                ybr = float(box.get("ybr"))

                # Obliczenia YOLO (x_center, y_center, w, h) - znormalizowane
                box_w = xbr - xtl
                box_h = ybr - ytl
                x_center = xtl + (box_w / 2)
                y_center = ytl + (box_h / 2)

                # Normalizacja
                x_c_norm = x_center / width
                y_c_norm = y_center / height
                w_norm = box_w / width
                h_norm = box_h / height

                # Klasa 0 = tablica
                yolo_lines.append(
                    f"0 {x_c_norm:.6f} {y_c_norm:.6f} {w_norm:.6f} {h_norm:.6f}"
                )

        # Zapisujemy dane tylko jeśli są jakieś ramki
        if yolo_lines:
            data_map[file_name] = yolo_lines

    return data_map


def setup_directories():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    for split in ["train", "val"]:
        for type_ in ["images", "labels"]:
            os.makedirs(os.path.join(OUTPUT_DIR, split, type_), exist_ok=True)


def main():
    print(f"Parsowanie pliku: {XML_FILE}")
    if not os.path.exists(XML_FILE):
        print(
            "BŁĄD: Nie znaleziono pliku annotations.xml! Sprawdź ścieżkę data/annotations/annotations.xml"
        )
        return

    # 1. Przetworzenie XML do pamięci
    labels_map = parse_cvat_xml(XML_FILE)
    print(f"Znaleziono etykiety dla {len(labels_map)} zdjęć.")

    # 2. Lista dostępnych zdjęć na dysku
    available_images = [
        f for f in os.listdir(IMAGES_DIR) if f.lower().endswith((".jpg", ".png"))
    ]

    # Filtrujemy tylko te, które mają etykiety
    valid_images = [img for img in available_images if img in labels_map]

    if not valid_images:
        print("BŁĄD: Nazwy plików w XML nie pasują do plików w folderze data/images!")
        print(
            "Przykładowa nazwa w XML:",
            list(labels_map.keys())[0] if labels_map else "Brak",
        )
        print(
            "Przykładowa nazwa na dysku:",
            available_images[0] if available_images else "Brak",
        )
        return

    # 3. Podział na Train/Val
    train_imgs, val_imgs = train_test_split(
        valid_images, test_size=0.3, random_state=42
    )

    # 4. Kopiowanie plików i tworzenie .txt
    for split_name, img_list in [("train", train_imgs), ("val", val_imgs)]:
        print(f"Generowanie zbioru {split_name}...")
        for img_filename in tqdm(img_list):
            # Ścieżki źródłowe
            src_img_path = os.path.join(IMAGES_DIR, img_filename)

            # Ścieżki docelowe
            dst_img_path = os.path.join(OUTPUT_DIR, split_name, "images", img_filename)
            dst_label_path = os.path.join(
                OUTPUT_DIR,
                split_name,
                "labels",
                os.path.splitext(img_filename)[0] + ".txt",
            )

            # Kopiowanie zdjęcia
            shutil.copy(src_img_path, dst_img_path)

            # Zapis etykiet txt
            with open(dst_label_path, "w") as f:
                f.write("\n".join(labels_map[img_filename]))

    # 5. Generowanie data.yaml
    abs_path = os.path.abspath(OUTPUT_DIR).replace("\\", "/")
    yaml_content = f"""
path: {abs_path}
train: train/images
val: val/images
names:
  0: license_plate
"""
    with open("../data.yaml", "w") as f:
        f.write(yaml_content)

    print("GOTOWE! Uruchom 2_train.py")


if __name__ == "__main__":
    main()
