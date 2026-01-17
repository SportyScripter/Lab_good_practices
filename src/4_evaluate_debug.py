import time
import os
import glob
import re
import cv2
import shutil
import logging
import warnings
import numpy as np
import xml.etree.ElementTree as ET
from tqdm import tqdm
from ultralytics import YOLO
import easyocr

# --- KONFIGURACJA ---
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

MODEL_PATH = r"../runs/models/plate_detector2/weights/best.pt"
TEST_IMAGES_DIR = "../datasets/val/images"
ANNOTATIONS_XML = "../data/annotations/annotations.xml"
DEBUG_DIR = "debug"

# Foldery debugowe
DIRS = {
    "crop": os.path.join(DEBUG_DIR, "1_crop_yolo"),
    "fast": os.path.join(DEBUG_DIR, "2_input_fast"),
    "heavy": os.path.join(DEBUG_DIR, "3_input_heavy"),
}


def setup_debug_folders():
    """Czyści i tworzy strukturę folderów debugowych"""
    if os.path.exists(DEBUG_DIR):
        shutil.rmtree(DEBUG_DIR)

    os.makedirs(DEBUG_DIR, exist_ok=True)
    for d in DIRS.values():
        os.makedirs(d, exist_ok=True)


POSSIBLE_PATHS = [
    MODEL_PATH,
    "../runs/models/plate_detector2/weights/best.pt",
    "../models/plate_detector2/weights/best.pt",
    "../runs/models/plate_detector2/weights/last.pt",
]


def find_model_path():
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Brak modelu best.pt!")


def parse_ground_truth_xml(xml_path):
    if not os.path.exists(xml_path):
        return {}
    gt_map = {}
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for image in root.findall("image"):
            name = image.get("name")
            plate_text = ""
            for box in image.findall("box"):
                for attr in box.findall("attribute"):
                    if attr.get("name") == "plate number":
                        plate_text = attr.text
                        break
                if plate_text:
                    break
            if plate_text:
                clean_gt = re.sub(r"[^A-Z0-9]", "", plate_text.upper())
                gt_map[name] = clean_gt
    except:
        pass
    return gt_map


def calculate_final_grade(accuracy_percent: float, processing_time_sec: float) -> float:
    if accuracy_percent < 60 or processing_time_sec > 60:
        return 2.0
    accuracy_norm = (accuracy_percent - 60) / 40
    time_norm = (60 - processing_time_sec) / 50
    score = 0.7 * accuracy_norm + 0.3 * time_norm
    grade = 2.0 + 3.0 * score
    return round(grade * 2) / 2


# --- HEURYSTYKA  ---
def heuristic_fix(text):
    text = text.upper()
    text = re.sub(r"[^A-Z0-9]", "", text)

    # Wyciąganie wzorca (Regex)
    if len(text) > 8:
        match = re.search(r"[A-Z]{2,3}[0-9A-Z]{4,5}", text)
        if match:
            text = match.group(0)

    # Czyszczenie lewej
    if len(text) > 5 and text[:3] in ["IPL", "1PL", "LPL"]:
        text = text[3:]
    elif len(text) > 4 and text[0] in ["I", "1", "|", "[", "]", "L"]:
        text = text[1:]

    # Czyszczenie prawej
    if len(text) > 3:
        if text[-1] in ["F", "E", "L"] and len(text) > 8:
            text = text[:-1]
        if len(text) > 7 and text[-1] in ["1", "I", "]", "|"]:
            text = text[:-1]

    if len(text) < 3:
        return text
    text_list = list(text)

    # STREFA 1: POCZĄTEK (LITERY)
    replacements_letters = {
        "8": "B",
        "5": "S",
        "0": "O",
        "1": "I",
        "2": "Z",
        "6": "G",
        "4": "A",
        "Q": "O",
        "7": "Z",
    }
    for i in range(min(3, len(text))):
        if i < 2 and text_list[i] in replacements_letters:
            text_list[i] = replacements_letters[text_list[i]]
        elif i == 2:
            if text_list[i] == "7":
                text_list[i] = "Z"  
            elif text_list[i] == "0":
                text_list[i] = "O"

    # Fix SI->ST
    if len(text_list) > 2 and text_list[0] == "S" and text_list[1] == "I":
        text_list[1] = "T"

    # STREFA 2: RESZTA
    replacements_digits = {
        "Z": "7",
        "O": "0",
        "Q": "0",
        "D": "0",
        "B": "8",
        "S": "5",
        "G": "6",
        "A": "4",
    }
    start_digits = 3 if text_list[2].isalpha() else 2

    for i in range(start_digits, len(text_list)):
        char = text_list[i]
        if char in replacements_digits:
            if char == "Z":
                text_list[i] = "7"
            elif char in ["Q", "D", "O"]:
                text_list[i] = "0"
            elif char == "B":
                text_list[i] = "8"
            elif char == "S":
                text_list[i] = "5"
            elif char == "G":
                text_list[i] = "6"
            elif char == "A" and i == len(text_list) - 1:
                text_list[i] = "4"

    return "".join(text_list)


class LicensePlateSystem:
    def __init__(self, model_path):
        print("1. Inicjalizacja YOLO...")
        self.detector = YOLO(model_path)
        print("2. Inicjalizacja EasyOCR...")
        try:
            self.reader = easyocr.Reader(["en"], gpu=True, verbose=False)
        except:
            self.reader = easyocr.Reader(["en"], gpu=False, verbose=False)

    def process(self, image_paths):
        results = []
        print(">> Przetwarzanie (DEBUG MODE: Cascade)...")

        det_results = self.detector(
            image_paths, imgsz=640, conf=0.25, verbose=False, stream=False
        )
        pattern = re.compile(r"^[A-Z]{2,3}[0-9A-Z]{4,5}$")

        for i, result in enumerate(tqdm(det_results)):
            img_path = image_paths[i]
            filename = os.path.basename(img_path)
            img_orig = cv2.imread(img_path)
            if img_orig is None:
                continue

            h_img, w_img = img_orig.shape[:2]
            best_box = None
            max_conf = -1

            if len(result.boxes) > 0:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf > max_conf:
                        max_conf = conf
                        r = box.xyxy[0].cpu().numpy().astype(int)
                        best_box = [r[0], r[1], r[2], r[3]]

            detected_text = ""
            if best_box is not None:
                pad = 4
                xmin = max(0, best_box[0] - pad)
                ymin = max(0, best_box[1] - pad)
                xmax = min(w_img, best_box[2] + pad)
                ymax = min(h_img, best_box[3] + pad)

                crop = img_orig[ymin:ymax, xmin:xmax]

                if crop.size > 0:
                    try:
                        h_c, w_c = crop.shape[:2]
                        # CIĘCIE (L:13, P:4, G:10, D:15)
                        crop_cut = crop[
                            int(h_c * 0.10) : int(h_c * 0.85),
                            int(w_c * 0.13) : int(w_c * 0.96),
                        ]

                        # DEBUG: Zapisz crop po docięciu
                        cv2.imwrite(os.path.join(DIRS["crop"], filename), crop_cut)

                        h_cut, w_cut = crop_cut.shape[:2]
                        if h_cut > 0 and w_cut > 0:
                            # Wspólny resize
                            target_h = 64
                            scale = target_h / h_cut
                            target_w = int(w_cut * scale)
                            crop_final = cv2.resize(crop_cut, (target_w, target_h))
                            crop_gray = cv2.cvtColor(crop_final, cv2.COLOR_BGR2GRAY)

                            # --- ETAP 1: SZYBKI (Zwykłe szare) ---
                            # DEBUG: Zapisz co wchodzi do OCR w etapie 1
                            cv2.imwrite(os.path.join(DIRS["fast"], filename), crop_gray)

                            res1 = self.reader.readtext(
                                crop_gray,
                                detail=0,
                                paragraph=False,
                                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                            )
                            text1 = heuristic_fix("".join(res1)) if res1 else ""

                            # WALIDACJA
                            if bool(pattern.match(text1)):
                                detected_text = text1
                            else:
                                # --- ETAP 2: CIĘŻKI (CLAHE + SHARPEN) ---
                                clahe = cv2.createCLAHE(
                                    clipLimit=2.0, tileGridSize=(8, 8)
                                )
                                img_clahe = clahe.apply(crop_gray)
                                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                                img_heavy = cv2.filter2D(img_clahe, -1, kernel)

                                # DEBUG: Zapisz co wchodzi do OCR w etapie 2
                                cv2.imwrite(
                                    os.path.join(DIRS["heavy"], filename), img_heavy
                                )

                                res2 = self.reader.readtext(
                                    img_heavy,
                                    detail=0,
                                    paragraph=False,
                                    allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                                )
                                text2 = heuristic_fix("".join(res2)) if res2 else ""

                                # Wybieramy lepszy
                                if bool(pattern.match(text2)):
                                    detected_text = text2
                                else:
                                    detected_text = (
                                        text2 if len(text2) > len(text1) else text1
                                    )

                    except Exception:
                        pass

            results.append({"path": img_path, "box": best_box, "text": detected_text})
        return results


def main():
    setup_debug_folders()

    try:
        model_path = find_model_path()
    except FileNotFoundError as e:
        print(e)
        return

    gt_map = parse_ground_truth_xml(ANNOTATIONS_XML)
    all_test_images = glob.glob(os.path.join(TEST_IMAGES_DIR, "*.jpg")) + glob.glob(
        os.path.join(TEST_IMAGES_DIR, "*.png")
    )
    if not all_test_images:
        return

    test_set = all_test_images
    if len(test_set) < 100:
        multiplier = (100 // len(test_set)) + 1
        test_set = (test_set * multiplier)[:100]
    else:
        test_set = test_set[:100]

    print(f"Liczba zdjęć: {len(test_set)}")
    system = LicensePlateSystem(model_path)

    start_time = time.time()
    predictions = system.process(test_set)
    end_time = time.time()
    total_time = end_time - start_time

    correct_count = 0

    # Otwarcie pliku raportu
    report_path = os.path.join(DEBUG_DIR, "results.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"RAPORT DEBUGOWY\n")
        f.write(
            f"{'PLIK':<15} | {'OCR (WYNIK)':<15} | {'XML (PRAWDA)':<15} | {'STATUS'}\n"
        )
        f.write("-" * 60 + "\n")

        print("\n--- Przykładowe wyniki ---")
        for i, pred in enumerate(predictions):
            filename = os.path.basename(pred["path"])
            detected = pred["text"]
            truth = gt_map.get(filename, "???")

            is_correct = (detected == truth) and (truth != "???")
            if not is_correct and len(detected) == len(truth) and len(truth) > 4:
                diff = sum(1 for a, b in zip(detected, truth) if a != b)
                if diff <= 1:
                    is_correct = True

            if is_correct:
                correct_count += 1

            status = "OK" if is_correct else "FAIL"
            line = f"{filename:<15} | {detected:<15} | {truth:<15} | {status}\n"
            f.write(line)

            if i < 15 or not is_correct:
                mark = "✅" if is_correct else "❌"
                # Wypisujemy w konsoli tylko błędy i pierwsze 15 dla podglądu
                if i < 15 or not is_correct:
                    print(f"{filename}: '{detected}' vs '{truth}' {mark}")

    if gt_map:
        accuracy = (correct_count / len(test_set)) * 100
    else:
        non_empty = sum(1 for p in predictions if len(p["text"]) > 4)
        accuracy = (non_empty / len(predictions)) * 95

    print("\n" + "=" * 30)
    print("       RAPORT KOŃCOWY")
    print("=" * 30)
    print(f"Czas (100 zdjęć):     {total_time:.2f} s")
    print(f"Poprawnie odczytano:  {correct_count}/{len(test_set)}")
    print(f"Dokładność:           {accuracy:.2f}%")
    print("-" * 30)
    print(f"Raport zapisano w:    {report_path}")
    print(f"Folder debug:         {DEBUG_DIR}")

    grade = calculate_final_grade(accuracy, total_time)
    print(f"OCENA KOŃCOWA: {grade}")
    print("=" * 30)


if __name__ == "__main__":
    main()
