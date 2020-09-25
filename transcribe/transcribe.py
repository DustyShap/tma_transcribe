from __future__ import print_function
import requests
import boto3
from tempfile import NamedTemporaryFile
from botocore.exceptions import ClientError



class TranscribeJob():
    def __init__(self):
        self.job_name = self._get_job_name()
        self.job_url = self._get_job_url()
        self.transcribe = boto3.client('transcribe', region_name='us-west-2')
        self.s3 = boto3.resource('s3')
        self.s3_key = None

    @property
    def s3_bucket(self):
        return 'tmatranscribe'

    def _get_job_name(self):
        return input("What is the name of this job?: ").strip()

    def _get_job_url(self):
        return input("What is the url of the audio file?: ")

    def upload_audio_to_s3(self):
        r = requests.get(self.job_url)
        if r.status_code == 200:
            with NamedTemporaryFile(mode='wb') as f:
                f.write(r.content)
                self.s3.Bucket(self.s3_bucket).upload_file(f.name, f"{self.job_name}.mp3")
        else:
            print(f"Failed to download {self.job_url}")

    def transcribe_from_s3(self):
        self.transcribe.start_transcription_job(
                TranscriptionJobName=self.job_name,
                Media={"MediaFileUri": f"s3://{self.s3_bucket}/{self.job_name}.mp3"},
                OutputBucketName='tmatranscribe',
                OutputKey=f'completed_transcriptions/{self.job_name}.json',
                MediaFormat="mp3",
                LanguageCode="en-US"
        )




if __name__ == "__main__":
    transcribe = TranscribeJob()
    transcribe.upload_audio_to_s3()
    transcribe.transcribe_from_s3()
