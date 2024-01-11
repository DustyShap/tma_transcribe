import os
import psycopg2

from dotenv import load_dotenv


load_dotenv()
class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT'],
        )

    def is_segment_exists(self, title):
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM transcriptions WHERE segment_title = %s", (title,))
            count = cur.fetchone()[0]
            return count > 0

    def insert_transcription(self, text, title, url, pub_date, segment_summary):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO transcriptions (transcribed_text, segment_title, segment_url, segment_pub_date, segment_summary)
                VALUES (%s, %s, %s, %s, %s)
            """, (text, title, url, pub_date, segment_summary))
            self.conn.commit()