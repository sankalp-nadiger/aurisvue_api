import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .utils import preprocess_text, load_video_file_names, analyze_with_gemini, analyze_with_openai, analyze_with_claude
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware
import requests
import ast
import re
import ollama
import hashlib
import json


app = FastAPI()

# Add the CORSMiddleware to FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)

VIDEO_FILE_PATH = "app/video_file_names.txt"
video_files = load_video_file_names(VIDEO_FILE_PATH)

class TranscriptInput(BaseModel):
    transcript: str


CACHE_DIR = "cache_json"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(transcript: str):
    key = hashlib.sha256(transcript.strip().lower().encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{key}.json")


@app.post("/analyze/")
def analyze_transcript(data: TranscriptInput):
    try:
        cache_path = get_cache_path(data.transcript)

        # If cache exists, use it
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)

        # Otherwise generate
        relevant = analyze_with_gemini(data.transcript, video_files)

        result = {"videos": relevant}

        # Save to cache
        with open(cache_path, "w") as f:
            json.dump(result, f)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze_mistral/")
def analyze_with_mistral(data: TranscriptInput):
    print("Analyze mistral")
    try:
        prompt = f"""
You're the fastest semantic search expert. Given the cleaned transcript:

"{data.transcript}"

Determine the most relevant videos from the list below using faster techniques and give response as fast you can (i.e., quickly narrow down using semantic decisions):

{', '.join(video_files)}

Return ONLY a Python list of filenames in this format:
["video1.mp4", "video2.mp4"]
Give only one file name for one word and if not matched then go letter by letter.
"""

        response = ollama.chat(
            model="mistral",  # or any other installed local model
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )

        content = response['message']['content']
        match = re.search(r'\[(.*?)\]', content, re.DOTALL)
        if match:
            list_str = "[" + match.group(1) + "]"
            parsed = ast.literal_eval(list_str)
            return {"videos": [f for f in parsed if f in video_files]}
        return {"videos": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/analyze_openai/")
# def analyze_with_openai_api(data: TranscriptInput):
#     print("Analyze OpenAI")
#     try:
#         relevant = analyze_with_openai(data.transcript, video_files)
#         return {"videos": relevant}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/analyze_claude/")
# def analyze_with_claude_api(data: TranscriptInput):
#     print("Analyze Claude")
#     try:
#         relevant = analyze_with_claude(data.transcript, video_files)
#         return {"videos": relevant}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


