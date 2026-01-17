import os
from ultralytics import YOLO

# Wznawianie treningu z ostatniego zapisanego stanu
def resume_training():
    # Ścieżka do pliku last.pt z poprzedniego treningu
    path_to_last = "../runs/models/plate_detector2/weights/last.pt"


    if not os.path.exists(path_to_last):
        print(f"BŁĄD: Nie widzę pliku {path_to_last}")
        print("Znajdź plik last.pt ręcznie i wklej jego ścieżkę w kodzie.")
        return

    print(f"Wznawiam trening z pliku: {path_to_last}")
    model = YOLO(path_to_last)
    model.train(resume=True)


if __name__ == "__main__":
    resume_training()
