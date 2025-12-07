import uuid
from db_config import cur, con

DB_FILE = "task.csv"


def add_task():
    task_id = str(uuid.uuid4())
    status = "pending"
    cur.execute("INSERT INTO tasks (id, status) VALUES (?, ?)", (task_id, status))
    con.commit()


if __name__ == "__main__":
    print(
        "Ile zadań chcesz dodać? (Wpisz 1 dla pojedenczyego zadania lub większą liczbę dla wielu zadań)"
    )
    count = int(input("Liczba zadań: "))
    for _ in range(count):
        add_task()

for row in cur.execute("SELECT * FROM tasks"):
    print(row)
con.close()
