import redis
import sqlite3
import time
import json
import os
from src.ocr_engine import LicensePlateSystem

# Konfiguracja
REDIS_HOST = os.getenv(
    "REDIS_HOST", "localhost"
)  # Czyta z ENV, jak nie ma to localhost
QUEUE_NAME = "alpr_queue"
DB_NAME = "plates.db"


def init_db():
    """Tworzy prostą tabelę w SQLite jeśli nie istnieje"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS plate_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            original_name TEXT,
            detected_text TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()
    print(">> [WORKER] Baza danych SQLite gotowa.")


def main():
    # 1. Połącz z bazą i Redisem
    init_db()
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
        r.ping()
        print(">> [WORKER] Połączono z Redisem. Czekam na zadania...")
    except:
        print(
            ">> [WORKER] BŁĄD: Brak Redisa! Uruchom: docker run -d -p 6379:6379 redis"
        )
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "best.pt")

    # Jeśli plik nie istnieje (np. lokalnie), spróbuj starej ścieżki (dla kompatybilności)
    if not os.path.exists(model_path):
        model_path = "../runs/models/plate_detector2/weights/best.pt"

    ocr_system = LicensePlateSystem(model_path=model_path)

    # 3. Pętla nieskończona (nasłuchiwanie)
    while True:
        # blpop blokuje skrypt i czeka na element w liście (oszczędza CPU)
        # Zwraca krotkę (nazwa_kolejki, dane)
        task = r.blpop(QUEUE_NAME, timeout=0)

        if task:
            raw_data = task[1]
            data = json.loads(raw_data)

            task_id = data["task_id"]
            file_path = data["file_path"]
            original_name = data["original_name"]

            print(f"--> Przetwarzam zadanie: {task_id} ({original_name})")

            # Analiza
            try:
                plate_text = ocr_system.process_image(file_path)
                print(f"    WYNIK: {plate_text}")

                # Zapis do bazy
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute(
                    "INSERT INTO plate_results (task_id, original_name, detected_text) VALUES (?, ?, ?)",
                    (task_id, original_name, plate_text),
                )
                conn.commit()
                conn.close()
                print("    [OK] Zapisano w bazie.")

            except Exception as e:
                print(f"    [BŁĄD] {e}")


if __name__ == "__main__":
    main()
