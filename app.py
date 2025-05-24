from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, TranscriptSummary
from utils import youtube_to_transcript_and_summary
import os
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = summary = title = error = None

    if request.method == "POST":
        url = request.form.get("youtube_url")
        try:
            transcript, summary, title = youtube_to_transcript_and_summary(url)

            if transcript and summary:
                # Store in DB
                entry = TranscriptSummary(
                    youtube_url=url,
                    title=title,
                    transcript=transcript,
                    summary=summary
                )
                db.session.add(entry)
                db.session.commit()
                return redirect(url_for("result", entry_id=entry.id))
            else:
                flash("Failed to process video.", "danger")
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("index.html")

@app.route("/result/<int:entry_id>")
def result(entry_id):
    entry = TranscriptSummary.query.get_or_404(entry_id)
    return render_template("index.html", transcript=entry.transcript, summary=entry.summary, title=entry.title)

if __name__ == "__main__":
    app.run(debug=True)