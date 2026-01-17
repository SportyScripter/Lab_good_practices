from fastapi import FastAPI, UploadFile, File
import shutil
import os
import redis
import uuid
import json
from src.ocr_engine import LicensePlateSystem

app = FastAPI(title="ALPR System API")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

# Połączenie z Redisem
try:
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    r.ping()
    print(">> [API] Połączono z Redisem")
except:
    print(">> [API] BŁĄD: Nie można połączyć z Redisem! Upewnij się, że Docker działa.")

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "best.pt")

if not os.path.exists(model_path):
    model_path = "../runs/models/plate_detector2/weights/best.pt"

ocr_system = LicensePlateSystem(model_path=model_path)
os.makedirs("uploads", exist_ok=True)


# 1. Endpoint Synchroniczny (wynik odrazu)
@app.post("/predict")
async def predict_sync(file: UploadFile = File(...)):
    temp_filename = f"uploads/sync_{uuid.uuid4()}.jpg"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ocr_system.process_image(temp_filename)


    return {"filename": file.filename, "plate_detected": result}


# 2. Endpoint Asynchroniczny (Na kolejkę)
@app.post("/queue-image")
async def queue_image(file: UploadFile = File(...)):
    # Unikalne ID zadania
    task_id = str(uuid.uuid4())
    file_path = f"uploads/async_{task_id}.jpg"

    # Zapisz plik na dysku
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    #  dane dla Workera
    task_data = json.dumps(
        {"task_id": task_id, "file_path": file_path, "original_name": file.filename}
    )

    try:
        r.rpush("alpr_queue", task_data)
        status = "queued"
    except:
        status = "error_redis"

    return {
        "task_id": task_id,
        "status": status,
        "message": "Zdjęcie zapisane i dodane do kolejki przetwarzania.",
    }
