import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for summarization
prompt = """You are a YouTube video summarizer. You will take the transcript text 
and summarize the entire video, providing the important points in a structured format within 500 words.
Please provide the summary of the text given here: """

# Function to extract YouTube video ID
def extract_video_id(url):
    """Extracts the YouTube video ID from various link formats."""
    match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

# Function to get transcript from YouTube
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            return None, "Invalid YouTube URL"

        # Attempt to fetch transcript
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry["text"] for entry in transcript_text])
        return transcript, None

    except TranscriptsDisabled:
        return None, "❌ Transcripts are disabled for this video."
    except NoTranscriptFound:
        return None, "⚠️ No transcript found for this video. It might not have captions."
    except Exception as e:
        return None, f"Error: {str(e)}"

# Function to generate summary using Gemini AI
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit UI
st.title("📺 YouTube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter YouTube video link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    else:
        st.error("Invalid YouTube URL. Please enter a valid link.")

if st.button("Get Detailed Notes"):
    transcript_text, error = extract_transcript_details(youtube_link)

    if error:
        st.error(error)
    elif transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## 📌 Detailed Notes:")
        st.write(summary)
    else:
        st.warning("No transcript found for this video.")
