from flask_sqlalchemy import SQLAlchemy
from sqlchemy.dialects.mysql import LONGTEXT

db = SQLAlchemy()

class Transcription(db.Model):
    __tablename__ = 'transcriptions'
    id = db.Column(db.Integer, primary_key=True)
    transcribed_text = db.Column(LONGTEXT)
    segment_title = db.Column(db.String, nullable=False)
    segment_url = db.Column(db.String, nullable=False)

