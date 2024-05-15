from flask import Flask, render_template, request
from sqlalchemy import desc, func, or_, and_
from models import Transcription
from create import create_app
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
app = create_app()
app.app_context().push()

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
    )
    return conn

def fetch_unique_years(cursor):
    cursor.execute("""
        SELECT DISTINCT EXTRACT(YEAR FROM segment_pub_date) AS year
        FROM transcriptions
        ORDER BY year DESC;
    """)
    return sorted({year[0] for year in cursor.fetchall()}, reverse=True)



@app.route('/')
def transcriptions():
    page = request.args.get('page', 1, type=int)  # Get the current page number, defaulting to 1
    per_page = 20  # Define how many items you want per page

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        unique_years = fetch_unique_years(cur)

        # Calculate the offset and limit for SQL query
        offset = (page - 1) * per_page

        # Fetch paginated transcriptions
        cur.execute("""
            SELECT * FROM transcriptions
            ORDER BY segment_pub_date DESC, segment_title ASC
            LIMIT %s OFFSET %s;
        """, (per_page, offset))
        transcriptions = cur.fetchall()

        # Get total count of transcriptions for pagination
        cur.execute("SELECT COUNT(*) FROM transcriptions")
        total_transcriptions = cur.fetchone()[0]

    finally:
        cur.close()
        conn.close()

    total_pages = (total_transcriptions + per_page - 1) // per_page  # Calculate total number of pages

    return render_template(
        'index.html',
        transcriptions=transcriptions,
        unique_years=unique_years,
        current_page=page,
        total_pages=total_pages
    )


@app.route('/search')
def search():
    queries = [request.args.get(f'query{i}', default='') for i in range(1, 6)]  # Support up to 5 queries
    year = request.args.get('year', type=int, default=None)
    month = request.args.get('month', type=int, default=None)
    day = request.args.get('day', type=int, default=None)

    page = request.args.get('page', 1, type=int)  # Current page
    per_page = 20  # Items per page

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        unique_years = fetch_unique_years(cur)

        # Construct base SQL query
        sql_query = "SELECT * FROM transcriptions WHERE 1=1"
        count_query = "SELECT COUNT(*) FROM transcriptions WHERE 1=1"
        params = []

        # Append conditions for queries
        for query in filter(None, queries):  # Skip empty queries
            sql_query += " AND transcribed_text ILIKE %s"
            count_query += " AND transcribed_text ILIKE %s"
            params.append(f'%{query}%')

        # Append conditions for year and month
        if year:
            sql_query += " AND EXTRACT(YEAR FROM segment_pub_date) = %s"
            count_query += " AND EXTRACT(YEAR FROM segment_pub_date) = %s"
            params.append(year)
        if month:
            sql_query += " AND EXTRACT(MONTH FROM segment_pub_date) = %s"
            count_query += " AND EXTRACT(MONTH FROM segment_pub_date) = %s"
            params.append(month)

        if year and month and day:
            sql_query += " AND segment_pub_date = DATE %s"
            count_query += " AND segment_pub_date = DATE %s"
            # Construct the full date string YYYY-MM-DD
            full_date = f"{year}-{month:02d}-{day:02d}"
            params.append(full_date)
        # Fetch the count of relevant transcriptions
        cur.execute(count_query, params)
        total_results = cur.fetchone()[0]
        total_pages = (total_results + per_page - 1) // per_page

        # Fetch the relevant transcriptions
        sql_query += " ORDER BY segment_pub_date DESC, segment_title ASC LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        cur.execute(sql_query, params)
        transcriptions = cur.fetchall()

    finally:
        cur.close()
        conn.close()
    search_terms = ', '.join(filter(None, queries))
    search_description = f"Search results for: {search_terms}"
    if year:
        if month and day:
            # Year, month, and day are specified
            search_description += f"{year}-{month:02d}-{day:02d}"
        elif month:
            # Only year and month are specified
            search_description += f" in {month}/{year}"
        else:
            # Only year is specified
            search_description += f" in {year}"
    return render_template('index.html', transcriptions=transcriptions, unique_years=unique_years,
                           total_pages=total_pages, current_page=page, queries=queries, year=year, month=month, search_description=search_description)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
