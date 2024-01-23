from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT

db = SQLAlchemy()

class Transcription(db.Model):
    __tablename__ = 'transcriptions'
    id = db.Column(db.Integer, primary_key=True)
    transcribed_text = db.Column(db.Text)
    segment_title = db.Column(db.String, nullable=False)
    segment_url = db.Column(db.String, nullable=False)
    segment_pub_date = db.Column(db.Date, nullable=False)
    segment_summary = db.Column(db.Text)
    segment_show_notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "transcribed_text": self.transcribed_text,
            "segment_title": self.segment_title,
            "segment_url": self.segment_url,
            "segment_pub_date": self.segment_pub_date,
            "segment_summary": self.segment_summary,
        }
