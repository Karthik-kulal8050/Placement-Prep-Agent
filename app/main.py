from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from .parse_inputs import read_pdf_text
from .analyze import agentic_gap_analysis
import tempfile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Placement Prep Agent")

class AnalyzeRequest(BaseModel):
    jd_text: str
    question: str = None

app.mount("/static", StaticFiles(directory="app/static"), name="static")
@app.get("/")
def serve_frontend():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(resume: UploadFile = File(...), jd_text: str = "", question: str = None):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await resume.read())
        tmp_path = tmp.name

    resume_text = read_pdf_text(tmp_path)
    result = agentic_gap_analysis(resume_text, jd_text, user_question=question)
    return result