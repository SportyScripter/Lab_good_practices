import os
import glob
import cv2
import logging
import warnings
from ultralytics import YOLO

# --- KONFIGURACJA ---
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Ścieżki
MODEL_PATH = r"../runs/models/plate_detector/weights/best.pt"
TEST_IMAGES_DIR = "../datasets/val/images"

def find_model_path():
    # Szukamy modelu w różnych typowych miejscach
    paths = [
        MODEL_PATH,
        "../runs/models/plate_detector/weights/best.pt",
        "../models/plate_detector/weights/best.pt",
        "../runs/detect/plate_detector/weights/best.pt",
        "runs/models/plate_detector/weights/best.pt"
    ]
    for p in paths:
        if os.path.exists(p): return p
    raise FileNotFoundError("Nie znaleziono modelu best.pt! Sprawdź folder 'runs'.")

def main():
    print("=== ROZPOCZYNAM DIAGNOSTYKĘ ===")
    
    # 1. Sprawdzenie modelu
    try:
        model_path = find_model_path()
        print(f"Model znaleziony: {model_path}")
        detector = YOLO(model_path)
    except Exception as e:
        print(f"BŁĄD MODELU: {e}")
        return

    # 2. Pobranie zdjęć
    images = glob.glob(os.path.join(TEST_IMAGES_DIR, "*.jpg")) + glob.glob(os.path.join(TEST_IMAGES_DIR, "*.png"))
    if not images:
        print(f"BŁĄD: Pusty folder {TEST_IMAGES_DIR}")
        return
    
    # Bierzemy pierwsze zdjęcie z brzegu
    test_img_path = images[0]
    print(f"Testuję na pliku: {os.path.abspath(test_img_path)}")
    
    # 3. Uruchomienie YOLO z BARDZO niskim progiem (conf=0.01)
    # Żeby zobaczyć czy cokolwiek wykrywa, nawet słabo
    print("Uruchamiam detekcję...")
    results = detector(test_img_path, conf=0.01, verbose=True)
    
    result = results[0]
    boxes = result.boxes
    
    print(f"\n--- WYNIKI DETEKCJI ---")
    print(f"Liczba wykrytych obiektów: {len(boxes)}")
    
    img = cv2.imread(test_img_path)
    
    if len(boxes) == 0:
        print("\n❌ ALARM: Model zwrócił 0 obiektów!")
        print("Przyczyny:")
        print("1. Trening się nie udał (puste pliki .txt w datasets/train/labels).")
        print("2. Model wczytuje się z innej ścieżki i jest pusty.")
    else:
        print("\n✅ SUKCES: Model działa!")
        for i, box in enumerate(boxes):
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            print(f" - Obiekt {i}: Pewność {conf:.2f}, Ramka {xyxy}")
            
            # Rysujemy ramkę
            cv2.rectangle(img, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 0, 255), 3)
            
            # Zapisujemy wycinek
            crop = img[xyxy[1]:xyxy[3], xyxy[0]:xyxy[2]]
            crop_name = f"debug_crop_{i}.jpg"
            cv2.imwrite(crop_name, crop)
            print(f"   -> Zapisano wycinek: {crop_name}")

    # Zapis całego zdjęcia z ramkami
    cv2.imwrite("debug_full.jpg", img)
    print(f"Zapisano pełny podgląd w: debug_full.jpg")

if __name__ == "__main__":
    main()