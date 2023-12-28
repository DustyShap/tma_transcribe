from flask import Flask, render_template, jsonify
from sqlalchemy import desc


from models import Transcription
from create import create_app

app = create_app()
app.app_context().push()

@app.route('/')
def hello_world():
    all_transcriptions = Transcription.query.order_by(desc(Transcription.segment_pub_date), Transcription.segment_title).all()

    transcription_list = [transcription for transcription in all_transcriptions]
    return render_template('index.html', transcriptions=transcription_list)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=8080)
