from flask import Flask, render_template, request
from sqlalchemy import desc, func
from models import Transcription
from create import create_app

app = create_app()
app.app_context().push()

@app.route('/')
def transcriptions():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Adjust as needed

    year_month_combinations = Transcription.query.with_entities(
        func.extract('year', Transcription.segment_pub_date).label('year'),
        func.extract('month', Transcription.segment_pub_date).label('month')
    ).distinct().order_by(
        desc(func.extract('year', Transcription.segment_pub_date)),
        desc(func.extract('month', Transcription.segment_pub_date))
    ).all()

    # Create a unique list of years
    unique_years = list(set([combo.year for combo in year_month_combinations]))
    unique_years.sort(reverse=True)  # Sort years in descending order

    paginated_transcriptions = Transcription.query.order_by(
        desc(Transcription.segment_pub_date),
        Transcription.segment_title
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'index.html',
        transcriptions=paginated_transcriptions.items,
        pagination=paginated_transcriptions,
        year_month_combinations=year_month_combinations,
        unique_years=unique_years  # Pass the unique years to the template
    )


@app.route('/search')
def search():
    query = request.args.get('query', default='')
    year = request.args.get('year', type=int, default=None)
    month = request.args.get('month', type=int, default=None)
    page = request.args.get('page', type=int, default=1)
    per_page = 20  # Adjust as needed

    # Base query with filters applied as per search parameters
    base_query = Transcription.query.filter(Transcription.transcribed_text.ilike(f'%{query}%'))
    if year:
        base_query = base_query.filter(func.extract('year', Transcription.segment_pub_date) == year)
    if month:
        base_query = base_query.filter(func.extract('month', Transcription.segment_pub_date) == month)

    paginated_transcriptions = base_query.order_by(desc(Transcription.segment_pub_date)).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('index.html', transcriptions=paginated_transcriptions.items, pagination=paginated_transcriptions, query=query, year=year, month=month)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
