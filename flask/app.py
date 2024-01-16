from flask import Flask, render_template, request
from sqlalchemy import desc
from models import Transcription
from create import create_app

app = create_app()
app.app_context().push()

@app.route('/')
def transcriptions():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Adjust as needed

    paginated_transcriptions = Transcription.query.order_by(desc(Transcription.segment_pub_date), Transcription.segment_title).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('index.html', transcriptions=paginated_transcriptions.items, pagination=paginated_transcriptions)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Adjust as needed

    paginated_transcriptions = Transcription.query.filter(
        Transcription.transcribed_text.ilike(f'%{query}%')
    ).order_by(desc(Transcription.segment_pub_date), Transcription.segment_title).paginate(
        page=page, per_page=per_page, error_out=False
    )
    no_results = not paginated_transcriptions.items
    return render_template('index.html', transcriptions=paginated_transcriptions.items, pagination=paginated_transcriptions, no_results=no_results, query=query)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
