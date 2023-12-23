from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import LONGTEXT

db = SQLAlchemy()

class Transcription(db.Model):
    __tablename__ = 'transcriptions'
    id = db.Column(db.Integer, primary_key=True)
    transcribed_text = db.Column(LONGTEXT)
    segment_title = db.Column(db.String, nullable=False)
    segment_url = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "transcribed_text": self.transcribed_text,
            "segment_title": self.segment_title,
            "segment_url": self.segment_url
        }