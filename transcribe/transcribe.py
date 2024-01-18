import concurrent.futures
import psycopg2
import requests
import sys
import whisper
import os
import tempfile


from datetime import datetime
from dotenv import load_dotenv

import xml.etree.ElementTree as ET
# from summarize import summarize_transcription


load_dotenv()

conn = psycopg2.connect(
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
    host=os.environ['POSTGRES_HOST'],
    port=os.environ['POSTGRES_PORT'],
)

def segment_exists(title):
    """Check if a segment with the given title already exists in the database."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM transcriptions WHERE segment_title = %s", (title,))
        count = cur.fetchone()[0]
        return count > 0

def insert_transcription(text, title, url, pub_date, segment_summary):
    """Insert a transcription into the database if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO transcriptions (transcribed_text, segment_title, segment_url, segment_pub_date, segment_summary)
            VALUES (%s, %s, %s, %s, %s)
        """, (text, title, url, pub_date, segment_summary))
        conn.commit()
        print(f"Inserted: {pub_date}")



def get_segments_for_date(feed_url, target_date):
    """Fetch segments from the RSS feed for a specific date."""
    response = requests.get(feed_url)
    root = ET.fromstring(response.content)

    # Parse the target_date into the desired format (YYYY-MM-DD)
    target_date_parsed = datetime.strptime(target_date, '%Y-%m-%d').strftime("%Y-%m-%d")

    segments = []
    for item in root.findall('.//item'):
        pub_date = item.find('pubDate').text

        # Parse the pub_date from the RSS feed into the desired format
        pub_date_parsed = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z').strftime("%Y-%m-%d")

        if target_date_parsed == pub_date_parsed:
            enclosure = item.find('enclosure')
            title = item.find('title').text
            if enclosure is not None and title is not None:
                segments.append((enclosure.get('url'), title, pub_date_parsed))

    return segments

def download_and_transcribe(url, title, pub_date):
    """Download an MP3 file, transcribe it, and insert into the database."""
    response = requests.get(url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
        temp_file.write(response.content)
        temp_file.flush()

        model = whisper.load_model("small.en")
        result = model.transcribe(temp_file.name, language="English", verbose=True, fp16=False)
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
        futures = []
        for url, title, pub_date in segments:
            if segment_exists(title):
                print(f"Segment with title '{title}' already exists in the database. Skipping.")
                continue
            print(f"Segment with title '{title}' does not exist in the database. Downloading and transcribing.")
            future = executor.submit(download_and_transcribe, url, title, pub_date)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print(f"Transcribed and uploaded: {target_date}")
            except Exception as e:
                print(f"An error occurred with {e}")

if __name__ == "__main__":
    main()
