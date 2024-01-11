from flask import Flask, render_template, request, jsonify
from sqlalchemy import desc
from models import Transcription
from create import create_app

app = create_app()
app.app_context().push()

@app.route('/')
def transcriptions():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Set the number of items per page

    paginated_transcriptions = Transcription.query.order_by(desc(Transcription.segment_pub_date)).paginate(page=page, per_page=per_page, error_out=False)
    transcription_list = [transcription for transcription in paginated_transcriptions.items]

    return render_template('index.html', transcriptions=transcription_list, pagination=paginated_transcriptions)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Set the number of items per page

    if query:
        paginated_transcriptions = Transcription.query.filter(Transcription.transcribed_text.like(f'%{query}%')).order_by(desc(Transcription.segment_pub_date)).paginate(page=page, per_page=per_page, error_out=False)

    else:
        # If no search query, just display the first page of all transcriptions
        paginated_transcriptions = Transcription.query.order_by(desc(Transcription.segment_pub_date)).paginate(page=page, per_page=per_page, error_out=False)

    no_results = True if not paginated_transcriptions.items else False

    return render_template('index.html', transcriptions=paginated_transcriptions.items, pagination=paginated_transcriptions, no_results=no_results, query=query)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

