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
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        unique_years = fetch_unique_years(cur)
        transcription_query = "SELECT * FROM transcriptions ORDER BY segment_pub_date DESC, segment_title LIMIT 100;"
        cur.execute(transcription_query)
        transcriptions = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    return render_template('index.html', transcriptions=transcriptions, unique_years=unique_years)


@app.route('/search')
def search():
    queries = [request.args.get(f'query{i}', default='') for i in range(1, 6)]  # Support for up to 5 queries
    year = request.args.get('year', type=int, default=None)
    month = request.args.get('month', type=int, default=None)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        unique_years = fetch_unique_years(cur)

        # Build the search query
        sql_query = "SELECT * FROM transcriptions WHERE 1=1"
        params = []

        for query in filter(None, queries):  # This ignores empty strings
            sql_query += " AND transcribed_text ILIKE %s"
            params.append(f'%{query}%')
        if year:
            sql_query += " AND EXTRACT(YEAR FROM segment_pub_date) = %s"
            params.append(year)
        if month:
            sql_query += " AND EXTRACT(MONTH FROM segment_pub_date) = %s"
            params.append(month)
        sql_query += " ORDER BY segment_pub_date DESC"

        cur.execute(sql_query, params)
        results = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    search_description = "Search results"
    if queries:
        search_description += " for: " + ", ".join(filter(None, queries))
    if year and month:
        search_description += f" in {month}/{year}"
    elif year:
        search_description += f" in {year}"

    return render_template('index.html', transcriptions=results, unique_years=unique_years, search_description=search_description)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
