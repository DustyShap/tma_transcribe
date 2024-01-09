import concurrent.futures
import psycopg2
import requests
import sys
import tempfile
import whisper
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

from summarize import summarize_transcription


load_dotenv()

conn = psycopg2.connect(
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
    host=os.environ['POSTGRES_HOST']
)

def insert_transcription(text, title, url, pub_date, segment_summary):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO transcriptions (transcribed_text, segment_title, segment_url, segment_pub_date, segment_summary)
            VALUES (%s, %s, %s, %s, %s)
        """, (text, title, url, pub_date, segment_summary))
        conn.commit()


def get_segments_for_date(feed_url, target_date):
    """Fetch segments from the RSS feed for a specific date."""
    response = requests.get(feed_url)
    root = ET.fromstring(response.content)
    target_date_formatted = datetime.strptime(target_date, '%Y-%m-%d').strftime("%a, %d %b %Y")

    segments = []
    for item in root.findall('.//item'):
        pub_date = item.find('pubDate').text
        if target_date_formatted in pub_date:
            enclosure = item.find('enclosure')
            title = item.find('title').text
            if enclosure is not None and title is not None:
                segments.append((enclosure.get('url'), title, pub_date))

    return segments

def download_and_transcribe(url, title, pub_date):
    """Download an MP3 file, transcribe it, and insert into the database."""
    response = requests.get(url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
        temp_file.write(response.content)
        temp_file.flush()

        model = whisper.load_model("small.en")
        result = model.transcribe(temp_file.name, language="English", verbose=True)
        # segment_summary = summarize_transcription(result['text'])
        segment_summary = 'None'
        # Insert into database
        insert_transcription(result['text'], title, url, pub_date, segment_summary)

def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
    feed_url = "https://feeds.megaphone.fm/tmastl"

    segments = get_segments_for_date(feed_url, target_date)
    if not segments:
        print(f"No segments found for {target_date}")
        return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_and_transcribe, url, title, pub_date) for url, title, pub_date in segments]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print(f"Transcribed and uploaded: {target_date}")
            except Exception as e:
                print(f"An error occurred with {e}")

if __name__ == "__main__":
    main()
