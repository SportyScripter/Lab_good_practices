import time
from db_config import cur, con

WORK_DURATION = 30
POLL_INTERVAL = 5


def process_task():

    while True:
        cur.execute("SELECT id FROM tasks WHERE status == 'pending' LIMIT 1")
        row = cur.fetchone()
        if row:
            taks_id = row[0]
            cur.execute(
                "UPDATE tasks SET status = 'in_progress' WHERE id = ?", (taks_id,)
            )
            print(f"[Consumer] Przetwarzanie zadania ID: {taks_id}...")
            cur.execute("UPDATE tasks SET status = 'done' WHERE id = ?", (taks_id,))
            con.commit()
            time.sleep(WORK_DURATION)
            print(f"[Consumer] Zadanie ID: {taks_id} zakończone.")
        else:
            print(
                f"[Consumer] Brak zadań do przetworzenia. Oczekiwanie {POLL_INTERVAL} sekund..."
            )
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    process_task()
