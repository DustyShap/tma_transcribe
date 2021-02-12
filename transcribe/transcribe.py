from __future__ import print_function
import datetime
import boto3
import feedparser
import re
import requests
import ssl
from tempfile import NamedTemporaryFile
from botocore.exceptions import ClientError

TMA_RSS_FEED = "https://tmastl.libsyn.com/rss"

def validate_date_input(date_string):
    return datetime.datetime.strptime(date_string, "%m/%d/%Y")

def entry_date_to_valid_string(date_string):
    date_obj = datetime.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")
    return datetime.datetime.strftime(date_obj, "%m/%d/%Y")

def url_to_filename(url, date):
    segment = re.findall(r'segment-[0-9]', url)[0]
    return f'{date}-{segment}.mp3'

ssl._create_default_https_context = ssl._create_unverified_context

class TranscribeJob():
    def __init__(self):
        self.date_input = self._get_date_input()
        self.job_urls = self._get_jobs_by_date()
        self.transcribe = boto3.client('transcribe', region_name='us-west-2')
        self.s3 = boto3.resource('s3')
        self.s3_key = None

    @property
    def s3_bucket(self):
        return 'tmatranscribe'

    def _get_date_input(self):
        date_string_input =  input("What is the date of the entries? (mm/dd/YYYY): ")
        try:
            validate_date_input(date_string_input)
        except:
            print(f"{date_string_input} is not a valid date format (mm/dd/YYYY)")
            exit()
        else:
            return date_string_input


    def _get_jobs_by_date(self):
        feed = feedparser.parse(TMA_RSS_FEED)
        urls = [entry.links[0].href for entry in feed.entries if entry_date_to_valid_string(entry.published) == self.date_input]
        urls.reverse()
        return urls

    def get_published_date(self):
        pass

    def upload_audio_to_s3(self):
        if not self.job_urls:
            print(f"No files found for the date {self.date_input}!")
            exit()
        for url in self.job_urls:
            print(url)
            # r = requests.get(url)
            # if r.status_code == 200:
            #     with NamedTemporaryFile(mode='wb') as f:
            #         f.write(r.content)
            #         self.s3.Bucket(self.s3_bucket).upload_file(f.name, url_to_filename(url, self.date_input))
            # else:
                # print(f"Failed to download {self.job_url}")

    def transcribe_from_s3(self):
        self.transcribe.start_transcription_job(
                TranscriptionJobName=self.job_name,
                Media={"MediaFileUri": f"s3://{self.s3_bucket}/{self.file_name}.mp3"},
                OutputBucketName='tmatranscribe',
                OutputKey=f'completed_transcriptions/{self.job_name}.json',
                MediaFormat="mp3",
                LanguageCode="en-US"
        )




if __name__ == "__main__":
    transcribe = TranscribeJob()
    transcribe.upload_audio_to_s3()
    # transcribe.transcribe_from_s3()
