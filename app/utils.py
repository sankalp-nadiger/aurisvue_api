import os
import string
import google.generativeai as genai
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def preprocess_text(text: str) -> str:
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return ' '.join([word for word in text.split() if word not in ENGLISH_STOP_WORDS])

def load_video_file_names(file_path: str):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def analyze_with_gemini(cleaned_text: str, video_files: list) -> list:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables")
        return 0

    genai.configure(api_key="AIzaSyB1R_hKDu2P9j0cD7b_ZM11xW8qz0AorDw")

    model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")
    
    prompt = f"""
    You are an intelligent assistant. Based on the following processed transcript:

    "{cleaned_text}"

    Determine which of the following video files are most relevant:

    {', '.join(video_files)}

    Return only a Python list of relevant filenames in this format:
    ["file1.mp4", "file2.mp4"]
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Debug the response
        print(f"Gemini response: {text[:100]}...")  # Print first 100 chars for debugging
        
        # Try to extract list from response - handle potential markdown code blocks
        if "```" in text:
            # Extract code from markdown code blocks if present
            import re
            code_match = re.search(r'```(?:python)?\s*(.*?)```', text, re.DOTALL)
            if code_match:
                text = code_match.group(1).strip()
        
        # Clean up potential list literals
        text = text.replace("'", '"')  # Replace single quotes with double quotes
        
        # Try direct list parsing first
        try:
            import ast
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                return [f for f in parsed if f in video_files]
        except Exception as e:
            print(f"First parse attempt failed: {e}")
            
            # Try extracting with regex as fallback
            import re
            matches = re.findall(r'"([^"]+\.mp4)"', text)
            if matches:
                return [f for f in matches if f in video_files]
            
    except Exception as e:
        print("Gemini error:", e)

    return video_files  # fallback
