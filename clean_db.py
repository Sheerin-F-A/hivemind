import sqlite3

def clean_db():
    conn = sqlite3.connect('hivemind.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM comments WHERE thread_title = 'Organic Personal Account History'")
    cursor.execute("DELETE FROM comments WHERE thread_title = 'Organic Personal Post'")
    conn.commit()
    print(f"Deleted {cursor.rowcount} buggy vault comments.")
    conn.close()

clean_db()
