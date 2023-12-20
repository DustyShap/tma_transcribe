#!/usr/bin/env python3
import concurrent.futures
import json
import requests
import sys
import tempfile
import whisper
import boto3
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

boto3.setup_default_session(aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                            region_name=os.environ.get("AWS_DEFAULT_REGION"))

def upload_to_s3(local_file_path, s3_bucket, s3_key):
    """Upload a file to an S3 bucket."""
    s3_client = boto3.client('s3')
    s3_client.upload_file(local_file_path, s3_bucket, s3_key)

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
                filename = title.replace(' ', '_') + '.json'
                segments.append((enclosure.get('url'), filename))

    return segments

def download_and_transcribe(url, output_filename, s3_bucket, s3_folder):
    """Download an MP3 file, transcribe it, write to JSON, and upload to S3."""
    response = requests.get(url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
        temp_file.write(response.content)
        temp_file.flush()

        model = whisper.load_model("medium")
        result = model.transcribe(temp_file.name, language="English", verbose=True)

        local_file_path = f"./{output_filename}"
        with open(local_file_path, 'w') as f:
            json.dump(result, f, indent=4)

        s3_key = f"{s3_folder}/{output_filename}"
        upload_to_s3(local_file_path, s3_bucket, s3_key)
        os.remove(local_file_path)

    return output_filename

def main():
    target_date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
    feed_url = "https://feeds.megaphone.fm/tmastl"
    s3_bucket = "tmatranscribe"
    s3_folder = f"whisper/{target_date}"

    segments = get_segments_for_date(feed_url, target_date)
    if not segments:
        print(f"No segments found for {target_date}")
        return

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_and_transcribe, url, filename, s3_bucket, s3_folder) for url, filename in segments]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                print(f"Transcribed and uploaded: {result}")
            except Exception as e:
                print(f"An error occurred with {e}")

if __name__ == "__main__":
    main()
