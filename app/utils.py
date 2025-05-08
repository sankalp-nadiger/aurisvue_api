import os
import string
import google.generativeai as genai
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from dotenv import load_dotenv
import ast
import re
import nltk
import openai
import anthropic
import requests
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords

# Ensure required NLTK resources are available
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('stopwords', quiet=True)

# Load environment variables
load_dotenv()

# Configure Gemini once
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_MODEL = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")
else:
    GEMINI_MODEL = None

# Configure OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

# Configure Anthropic client
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if ANTHROPIC_API_KEY:
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    anthropic_client = None

# Configure Hugging Face
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/phi-2"  # Using Phi-2 for speed

def preprocess_text(text: str) -> str:
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return ' '.join([word for word in text.split() if word not in ENGLISH_STOP_WORDS])

def load_video_file_names(file_path: str):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def fallback_noun_video_selection(text, video_files):
    words = [w for w in word_tokenize(text.lower()) if w.isalpha()]
    tagged = pos_tag(words)
    nouns = [w for w, tag in tagged if tag.startswith("NN") and w not in stopwords.words('english')]
    selected_letters = sorted(set(w[0].lower() for w in nouns))[:4]
    return [f for f in video_files if f[0].lower() in selected_letters]

def analyze_with_gemini(cleaned_text: str, video_files: list) -> list:
    print("Analyze gemini")
    if not GEMINI_MODEL:
        print("Warning: GEMINI_API_KEY not found")
        return fallback_noun_video_selection(cleaned_text, video_files)

    prompt = f"""
You are an expert in ultra-fast semantic search. Given the cleaned transcript below:

"{cleaned_text}"

Your goal is to select the most relevant video filenames from the **sorted list** below:

{', '.join(video_files)}

Instructions:
1. Perform a **semantic match** between the transcript and the video filenames/content. Use fast approximate matching and optimize search using **binary search** techniques since the list is sorted.
2. Try to find videos that match the **entire transcript** contextually or semantically.
3. If no full-context matches are found, fall back to selecting videos that correspond to **individual letters or words** in the transcript give videos for each of the letters (e.g., A.mp4, B.mp4).
4. Only return the most relevant videos (do not return all of them), formatted exactly like this:

["video1.mp4", "video2.mp4"]
"""


    try:
        response = GEMINI_MODEL.generate_content(prompt)
        text = response.text.strip()

        # Extract list if wrapped in markdown
        if "```" in text:
            match = re.search(r'```(?:python)?\s*(.*?)```', text, re.DOTALL)
            if match:
                text = match.group(1).strip()

        text = text.replace("'", '"')
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                result = [f for f in parsed if f in video_files]
                return result if result else fallback_noun_video_selection(cleaned_text, video_files)
        except Exception:
            matches = re.findall(r'"([^"]+\.mp4)"', text)
            if matches:
                return [f for f in matches if f in video_files]

    except Exception as e:
        print("Gemini error:", e)
    
    print("Finished analyze gemini")
    return fallback_noun_video_selection(cleaned_text, video_files)

def analyze_with_openai(cleaned_text: str, video_files: list) -> list:
    print("Starting OpenAI analysis")
    if not openai_client:
        print("Warning: OPENAI_API_KEY not found")
        return fallback_noun_video_selection(cleaned_text, video_files)

    # Using GPT-3.5-turbo for speed
    prompt = f"""
You're an expert in semantic search. Given this transcript:

"{cleaned_text}"

Find the most relevant videos from this list:
{', '.join(video_files)}

Instructions:
1. Match videos that relate to the transcript content semantically.
2. If no semantic matches, select videos starting with letters found in key words.
3. Keep response focused and fast.
4. Return EXACTLY in this format, nothing else:
["video1.mp4", "video2.mp4"]
"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are a fast semantic search assistant that returns only list results."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2, # Lower temperature for more deterministic, faster responses
            max_tokens=150
        )
        
        text = response.choices[0].message.content.strip()
        
        # Extract list if wrapped in markdown
        if "```" in text:
            match = re.search(r'```(?:python)?\s*(.*?)```', text, re.DOTALL)
            if match:
                text = match.group(1).strip()
        
        text = text.replace("'", '"')
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                result = [f for f in parsed if f in video_files]
                return result if result else fallback_noun_video_selection(cleaned_text, video_files)
        except Exception:
            matches = re.findall(r'"([^"]+\.mp4)"', text)
            if matches:
                return [f for f in matches if f in video_files]
    
    except Exception as e:
        print("OpenAI error:", e)
    
    print("Finished OpenAI analysis")
    return fallback_noun_video_selection(cleaned_text, video_files)

def analyze_with_claude(cleaned_text: str, video_files: list) -> list:
    print("Starting Claude analysis")
    if not anthropic_client:
        print("Warning: ANTHROPIC_API_KEY not found")
        return fallback_noun_video_selection(cleaned_text, video_files)

    prompt = f"""
As a lightning-fast semantic search specialist, analyze this transcript:

"{cleaned_text}"

Find the most relevant videos from this list:
{', '.join(video_files)}

Instructions:
1. Match videos that relate semantically to the transcript content.
2. If no clear semantic matches exist, select videos starting with letters found in key words.
3. Be extremely fast and focused with your analysis.
4. Return ONLY a Python list in this exact format - no explanations, no markdown:
["video1.mp4", "video2.mp4"]
"""

    try:
        response = anthropic_client.messages.create(
            model="claude-3-haiku-20240307",  # Using Claude Haiku for maximum speed
            max_tokens=100,
            temperature=0.2,
            system="You are a specialized semantic search tool that returns only a Python list of relevant video filenames.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        text = response.content[0].text.strip()
        
        # Extract list if wrapped in markdown
        if "```" in text:
            match = re.search(r'```(?:python)?\s*(.*?)```', text, re.DOTALL)
            if match:
                text = match.group(1).strip()
        
        text = text.replace("'", '"')
        try:
            parsed = ast.literal_eval(text)
            if isinstance(parsed, list):
                result = [f for f in parsed if f in video_files]
                return result if result else fallback_noun_video_selection(cleaned_text, video_files)
        except Exception:
            matches = re.findall(r'"([^"]+\.mp4)"', text)
            if matches:
                return [f for f in matches if f in video_files]
    
    except Exception as e:
        print("Claude error:", e)
    
    print("Finished Claude analysis")
    return fallback_noun_video_selection(cleaned_text, video_files)
