from flask import Flask, render_template, request, jsonify
from sqlalchemy import desc
from models import Transcription
from create import create_app

app = create_app()
app.app_context().push()

@app.route('/')
def hello_world():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Set the number of items per page

    paginated_transcriptions = Transcription.query.order_by(desc(Transcription.segment_pub_date), Transcription.segment_title).paginate(page, per_page, False)
    transcription_list = [transcription for transcription in paginated_transcriptions.items]

    return render_template('index.html', transcriptions=transcription_list, pagination=paginated_transcriptions)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
