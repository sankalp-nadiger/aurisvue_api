from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .utils import preprocess_text, load_video_file_names, analyze_with_gemini

app = FastAPI()

VIDEO_FILE_PATH = "app/video_file_names.txt"
video_files = load_video_file_names(VIDEO_FILE_PATH)

class TranscriptInput(BaseModel):
    transcript: str

@app.post("/analyze/")
def analyze_transcript(data: TranscriptInput):
    try:
        # cleaned = preprocess_text(data.transcript)
        relevant = analyze_with_gemini(data.transcript, video_files)
        return {"videos": relevant}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
