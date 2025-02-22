import sqlite3
from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")
OWNER_ID = int(getenv("OWNER_ID"))
CHANNEL_ID = int(getenv("CHANNEL_ID"))

START_URL = getenv("START_URL", "https://Skymovieshd.video")

class Database:
    def __init__(self, db_name="movies.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            link TEXT
        )""")
        self.conn.commit()

    def insert_movie(self, name, link):
        self.cursor.execute("INSERT OR IGNORE INTO movies (name, link) VALUES (?, ?)", (name, link))
        self.conn.commit()

    def get_recent_movies(self, limit=10):
        self.cursor.execute("SELECT name, link FROM movies ORDER BY id DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def is_movie_scraped(self, name):
        self.cursor.execute("SELECT name FROM movies WHERE name = ?", (name,))
        return self.cursor.fetchone() is not None

    def update_domain(self, new_url):
        global START_URL
        START_URL = new_url

db = Database()
