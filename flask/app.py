from flask import Flask, render_template

from models import Transcription
from create import create_app

app = create_app()
app.app_context().push()
@app.route('/')
def hello_world():
    all_transcriptions = Transcription.query.all()
    return render_template('index.html')

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8082)
