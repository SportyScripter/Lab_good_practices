import csv
import time
import os
import shutil
from tempfile import NamedTemporaryFile

DB_FILE = "task.csv"
WORK_DURATION = 30
POLL_INTERVAL = 5


def process_task():

    while True:
        task_to_process = None
        all_tasks = []
        found_pending = False
        try:
            if not os.path.exists(DB_FILE):
                print("[Consumer] Brak pliku z zadaniami.")
                time.sleep(POLL_INTERVAL)
                continue
            with open(DB_FILE, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                all_tasks = list(reader)
            for task in all_tasks:
                if task["status"] == "pending":
                    task["status"] = "in_progress"
                    task_to_process = task
                    found_pending = True
                    break
            if found_pending:
                with open(DB_FILE, mode="w", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=["id", "status"])
                    writer.writeheader()
                    writer.writerows(all_tasks)
                print(
                    f"[Consumer] Pobrałem zadanie {task_to_process['id']}. Praca w toku..."
                )
            else:
                print(
                    f"[Consumer] Brak zadań 'pending'. Ponowne sprawdzenie za {POLL_INTERVAL} sekund."
                )
                time.sleep(POLL_INTERVAL)
                continue
        except Exception as e:
            print(f"[Consumer] Błąd podczas odczytu/zapisu pliku: {e}")
            time.sleep(1)
            continue

        if task_to_process:
            time.sleep(WORK_DURATION)
            try:
                current_tasks = []
                with open(DB_FILE, mode="r", newline="") as file:
                    reader = csv.DictReader(file)
                    current_tasks = list(reader)

                for task in current_tasks:
                    if task["id"] == task_to_process["id"]:
                        task["status"] = "done"
                        break
                with open(DB_FILE, mode="w", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=["id", "status"])
                    writer.writeheader()
                    writer.writerows(current_tasks)
                print(
                    f"[Consumer] Zadanie {task_to_process['id']} zakończone sukcesem."
                )

            except Exception as e:
                print(f"[Consumer] Błąd przy zapisie statusu done: {e}")


if __name__ == "__main__":
    process_task()
