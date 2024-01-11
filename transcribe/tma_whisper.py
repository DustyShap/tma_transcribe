import concurrent.futures
import requests
import sys
import xml.etree.ElementTree as ET

from datetime import datetime

from db_manager import DatabaseManager
from transcription_manager import TranscriptionManager
class TMAWhisper:
    def __init__(self, feed_url):
        self.feed_url = feed_url
        self.db_manager = DatabaseManager()
        self.transcription_manager = TranscriptionManager()

    def get_segments_for_date(self, target_date):
        response = requests.get(self.feed_url)

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

    def process_segments(self, target_date):
        segments = self.get_segments_for_date(target_date)
        if not segments:
            print(f"No segments found for {target_date}")
            return

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for url, title, pub_date in segments:
                if self.db_manager.is_segment_exists(title):
                    print(f"Segment with title '{title}' already exists. Skipping.")
                    continue
                future = executor.submit(self.process_segment, url, title, pub_date)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    print(f"Transcribed and uploaded: {target_date}")
                except Exception as e:
                    print(f"An error occurred: {e}")

    def process_segment(self, url, title, pub_date):
        text = self.transcription_manager.download_and_transcribe(url)
        segment_summary = 'None'  # Placeholder for summary logic
        self.db_manager.insert_transcription(text, title, url, pub_date, segment_summary)

def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
    app = TMAWhisper("https://feeds.megaphone.fm/tmastl")
    app.process_segments(target_date)

if __name__ == "__main__":
    main()
