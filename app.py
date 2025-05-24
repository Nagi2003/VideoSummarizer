from fastapi import FastAPI, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from models import engine, SessionLocal, Base, TranscriptSummary
from utils import youtube_to_transcript_and_summary
import os
import dotenv

dotenv.load_dotenv()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse,name="home")
async def read_root(request: Request):
    flash_message = request.session.pop("flash", None)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "flash": flash_message
    })


@app.post("/", response_class=HTMLResponse,name="index")
async def submit_url(request: Request, youtube_url: str = Form(...)):
    db: Session = SessionLocal()
    try:
        transcript, summary, title = youtube_to_transcript_and_summary(youtube_url)

        if transcript and summary:
            entry = TranscriptSummary(
                youtube_url=youtube_url,
                title=title,
                transcript=transcript,
                summary=summary,
            )
            db.add(entry)
            db.commit()
            return RedirectResponse(url=f"/result/{entry.id}", status_code=status.HTTP_303_SEE_OTHER)
        else:
            request.session["flash"] = "Failed to process video."
    except Exception as e:
        request.session["flash"] = f"Error: {str(e)}"

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/result/{entry_id}", response_class=HTMLResponse)
async def result(request: Request, entry_id: int):
    db: Session = SessionLocal()
    entry = db.query(TranscriptSummary).get(entry_id)
    if not entry:
        return HTMLResponse("Not found", status_code=404)

    flash_message = request.session.pop("flash", None)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "transcript": entry.transcript,
        "summary": entry.summary,
        "title": entry.title,
        "flash": flash_message
    })
