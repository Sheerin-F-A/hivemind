import sqlite3
import json
import os

def export_db():
    if not os.path.exists('data/reddit_hive.db'):
        print("Database not found. Make sure to log in through the UI first!")
        return
        
    conn = sqlite3.connect('data/reddit_hive.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, comment_id, subreddit, thread_id, thread_title, body, created_utc, score, sentiment_score, sentiment_label, is_spam FROM comments")
        rows = cursor.fetchall()
    except Exception as e:
        print("Error exporting:", e)
        conn.close()
        return

    data = []
    for r in rows:
        data.append({
            "user_id": r[0],
            "comment_id": r[1],
            "subreddit": r[2],
            "thread_id": r[3],
            "thread_title": r[4],
            "body": r[5],
            "created_utc": r[6],
            "score": r[7],
            "sentiment_score": r[8],
            "sentiment_label": r[9],
            "is_spam": r[10]
        })
        
    with open('history.json', 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"Exported {len(data)} rows to history.json successfully.")
    conn.close()

if __name__ == "__main__":
    export_db()
