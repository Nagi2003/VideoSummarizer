from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TranscriptSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    youtube_url = db.Column(db.String(300), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    transcript = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
