import sqlite3


class Database:
    def __init__(self, db_name):
        self.cursor = None
        self.conn = None
        self.db_name = db_name
        self.connect_to_db()
        self.create_tables()
        self.close_connection()

    def connect_to_db(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close_connection(self):
        self.cursor.close()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT NOT NULL UNIQUE,
                          password TEXT NOT NULL)
                          ''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          price REAL NOT NULL,
                          quantity INTEGER NOT NULL)
                          ''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cart
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER,
                          product_id INTEGER,
                          quantity INTEGER,
                          FOREIGN KEY (user_id) REFERENCES users (id),
                          FOREIGN KEY (product_id) REFERENCES products (id))''')
        self.conn.commit()
