import requests
import tempfile
import whisper

class TranscriptionManager:
    def __init__(self):
        self.model = whisper.load_model("small.en")

    def download_and_transcribe(self, url):
        response = requests.get(url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
            temp_file.write(response.content)
            temp_file.flush()
            result = self.model.transcribe(temp_file.name, language="English", verbose=True, fp16=False)
            return result['text']