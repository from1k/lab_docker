import os
import mysql.connector

class ItemModel:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', os.getenv('DB_HOST')),
            'user': os.getenv('DB_USER', os.getenv('DB_USER')),
            'password': os.getenv('DB_PASS', os.getenv('DB_PASS')),
            'database': os.getenv('DB_NAME', os.getenv('DB_NAME'))
        }

    def get_all_items(self):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT name FROM items')
            items = cursor.fetchall()
            cursor.close()
            conn.close()
            return items
        except Exception as e:
            print(f"Error: {e}")
            return []

