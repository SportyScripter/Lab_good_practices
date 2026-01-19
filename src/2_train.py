from ultralytics import YOLO

def train():
    # Załadowanie modelu YOLOv8
    model = YOLO("yolov8n.pt")  # Ładujemy pretrenowany model YOLOv8n
    # Trenowanie modelu
    # imgsz=640 to standard
    # epochs=50 ilość epok do trenowania
    results = model.train(data="../data.yaml", epochs=50, imgsz=640, project="../models", name="plate_detector")
    
    # Walidacja (pokaże mAP i IoU)
    metrics = model.val()
    print(f"Map50: {metrics.box.map50}")
    print(f"Map50-95: {metrics.box.map}")

if __name__ == "__main__":
    train()