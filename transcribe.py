import requests
import whisper
import tempfile
import sys


def download_and_transcribe(url):
    """Download an MP3 file, transcribe it, and clean up."""
    # Download the file
    response = requests.get(url)
    response.raise_for_status()

    # Create a temporary file and transcribe
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
        temp_file.write(response.content)
        temp_file.flush()

        # Load and use the Whisper model
        model = whisper.load_model("medium")
        result = model.transcribe(temp_file.name, verbose=True)

    # Temporary file is automatically deleted here
    return result

def main():
    # Check if a URL argument is provided
    if len(sys.argv) < 2:
        print("Usage: python script.py <URL>")
        sys.exit(1)

    url = sys.argv[1]

    # Run the download and transcription
    try:
        transcription = download_and_transcribe(url)
        print(transcription["text"])
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
