import sqlite3

class db: 
    conn = None
    def __init__(self) -> None:
        self.conn = sqlite3.connect("messages.db", check_same_thread=False)
        try:
            cursor = self.conn.cursor()
            cursor.execute("""CREATE TABLE messages
                            (userID text, message text) 
                        """)
        except: pass

    def write_message(self, user_id, text) -> None:
        cursor = self.conn.cursor()
        print(f"INSERT INTO messages values ({user_id}, {text})")
        cursor.execute(f"INSERT INTO messages values ('{user_id}', '{text}')")
        self.conn.commit()

    def get_messages(self) -> None: # -> dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM messages")
        rows = cursor.fetchall()
        return list(reversed(rows))
