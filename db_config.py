import sqlite3

con = sqlite3.connect("task.db", timeout=10)
con.execute("PRAGMA journal_mode=WAL;")
cur = con.cursor()


def init_db():
    cur.execute("CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, status TEXT)")
    con.commit()


init_db()
