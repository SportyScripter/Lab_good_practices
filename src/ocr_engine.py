import cv2
import re
import numpy as np
import easyocr
from ultralytics import YOLO


class LicensePlateSystem:
    def __init__(self, model_path="best.pt"):
        print(">> [ENGINE] Ładowanie modelu YOLO...")
        self.detector = YOLO(model_path)
        print(">> [ENGINE] Ładowanie EasyOCR...")
        try:
            self.reader = easyocr.Reader(["en"], gpu=True, verbose=False)
        except:
            self.reader = easyocr.Reader(["en"], gpu=False, verbose=False)

        # Prekompilacja regexa
        self.pattern = re.compile(r"^[A-Z]{2,3}[0-9A-Z]{4,5}$")

    def heuristic_fix(self, text):
        text = text.upper()
        text = re.sub(r"[^A-Z0-9]", "", text)

        if len(text) > 8:
            match = re.search(r"[A-Z]{2,3}[0-9A-Z]{4,5}", text)
            if match:
                text = match.group(0)

        if len(text) > 5 and text[:3] in ["IPL", "1PL", "LPL"]:
            text = text[3:]
        elif len(text) > 4 and text[0] in ["I", "1", "|", "[", "]", "L"]:
            text = text[1:]

        if len(text) > 3:
            if text[-1] in ["F", "E", "L"] and len(text) > 8:
                text = text[:-1]
            if len(text) > 7 and text[-1] in ["1", "I", "]", "|"]:
                text = text[:-1]

        if len(text) < 3:
            return text
        text_list = list(text)

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

        if len(text_list) > 2 and text_list[0] == "S" and text_list[1] == "I":
            text_list[1] = "T"

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

    def process_image(self, img_path):
        """Metoda dla API/Workera - zwraca tekst tablicy lub NULL"""
        img_orig = cv2.imread(img_path)
        if img_orig is None:
            return None

        h_img, w_img = img_orig.shape[:2]

        # Detekcja 
        results = self.detector(img_orig, imgsz=640, conf=0.25, verbose=False)

        detected_text = "BRAK_TABLICY"
        best_box = None
        max_conf = -1

        for result in results:
            if len(result.boxes) > 0:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf > max_conf:
                        max_conf = conf
                        r = box.xyxy[0].cpu().numpy().astype(int)
                        best_box = [r[0], r[1], r[2], r[3]]

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

                    h_cut, w_cut = crop_cut.shape[:2]
                    if h_cut > 0 and w_cut > 0:
                        target_h = 64
                        scale = target_h / h_cut
                        target_w = int(w_cut * scale)
                        crop_final = cv2.resize(crop_cut, (target_w, target_h))
                        crop_gray = cv2.cvtColor(crop_final, cv2.COLOR_BGR2GRAY)

                        # Etap 1: Szybki
                        res1 = self.reader.readtext(
                            crop_gray,
                            detail=0,
                            paragraph=False,
                            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                        )
                        text1 = self.heuristic_fix("".join(res1)) if res1 else ""

                        # Walidacja i Etap 2 (Kaskada)
                        if bool(self.pattern.match(text1)):
                            detected_text = text1
                        else:
                            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                            img_clahe = clahe.apply(crop_gray)
                            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                            img_heavy = cv2.filter2D(img_clahe, -1, kernel)

                            res2 = self.reader.readtext(
                                img_heavy,
                                detail=0,
                                paragraph=False,
                                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                            )
                            text2 = self.heuristic_fix("".join(res2)) if res2 else ""
                            detected_text = text2 if len(text2) > len(text1) else text1
                except:
                    pass

        return detected_text
