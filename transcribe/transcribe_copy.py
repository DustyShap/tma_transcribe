import concurrent.futures
import psycopg2
import requests
import sys
import tempfile
import whisper
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv


load_dotenv()

conn = psycopg2.connect(
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD'],
    host=os.environ['POSTGRES_HOST']
)


def insert_transcription(text, title, url, pub_date):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO transcriptions (transcribed_text, segment_title, segment_url, segment_pub_date)
            VALUES (%s, %s, %s, %s)
        """, (text, title, url, pub_date))
        conn.commit()

def date_range(start_date, end_date):
    """Generate a range of dates from start_date to end_date."""
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

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

        # Insert into database
        insert_transcription(result['text'], title, url, pub_date)


def download_and_transcribe(url, title, pub_date):
    """Download an MP3 file, transcribe it, and insert into the database."""
    # ... [rest of the function]

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <start_date> <end_date>")
        sys.exit(1)

    start_date = datetime.strptime(sys.argv[1], '%Y-%m-%d')
    end_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
    feed_url = "https://feeds.megaphone.fm/tmastl"

    for single_date in date_range(start_date, end_date):
        formatted_date = single_date.strftime('%Y-%m-%d')
        segments = get_segments_for_date(feed_url, formatted_date)
        if not segments:
            print(f"No segments found for {formatted_date}")
            continue

        print(f"Segments found! Transcribing for date: {formatted_date}")
        print(segments)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_and_transcribe, url, title, pub_date) for url, title, pub_date in segments]
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    print(f"Transcribed and stored in database for date: {formatted_date}")
                except Exception as e:
                    print(f"An error occurred with {e}")

if __name__ == "__main__":
    main()
