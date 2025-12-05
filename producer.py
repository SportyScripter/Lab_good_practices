import csv
import uuid
import os

DB_FILE = "task.csv"


def add_task():
    task_id = str(uuid.uuid4())
    status = "pending"

    file_exists = os.path.isfile(DB_FILE)

    with open(DB_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["id", "status"])
        writer.writerow([task_id, status])
        print(f"[Producer] Dodano nowe zadanie: {task_id} z statusem '{status}'")


if __name__ == "__main__":
    print(
        "Ile zadań chcesz dodać? (Wpisz 1 dla pojedenczyego zadania lub większą liczbę dla wielu zadań)"
    )
    count = int(input("Liczba zadań: "))
    for _ in range(count):
        add_task()
