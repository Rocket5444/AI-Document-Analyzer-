# engine.py

import os
import streamlit as st
from pathlib import Path
# Suppressing Pylance warning for core SDK imports
from google import genai # type: ignore
from google.genai import types # type: ignore

# --- Gemini API Client Setup (Logic) ---

@st.cache_resource
def initialize_client():
    """Initializes the Gemini client securely using Streamlit Secrets."""
    # This function is cached, so the client is only created once.
    try:
        # 🔑 SECURE FIX: Read the API key from Streamlit Secrets
        api_key = st.secrets["GEMINI_API_KEY"]
        
        # Check for placeholder key (optional, but good practice)
        if api_key in ["YOUR_ACTUAL_API_KEY", ""]:
             raise KeyError("API key placeholder used.")
             
    except KeyError:
        return None, (
            "🛑KEY not found in Streamlit secrets. "
            "Please create a .streamlit/secrets.toml file and add your key."
        )

    try:
        client = genai.Client(api_key=api_key)
        return client, None
    except Exception as e:
        return None, f"Error initializing Gemini Client: {e}"


# --- Core Processing Functions (Logic) ---

@st.cache_resource
def upload_document(_client: genai.Client, uploaded_file_obj) -> types.File:
    """Uploads the file object to the Gemini File API."""
    file_name = uploaded_file_obj.name
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / file_name

    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file_obj.getbuffer())

    try:
        # _client is used to avoid hashing the unhashable Client object
        uploaded_file = _client.files.upload(
            file=str(temp_file_path)
        )
        return uploaded_file
    except Exception as e:
        st.error(f"Error during file upload: {e}")
        return None
    finally:
        # Clean up the local temporary file immediately
        os.remove(temp_file_path)
        if not os.listdir(temp_dir):
            os.rmdir(temp_dir)


def process_document(client: genai.Client, uploaded_file: types.File, prompt: str):
    """Sends the document and a prompt to the Gemini model."""
    
    contents = [uploaded_file, prompt]

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=contents
        )
        return response.text
    except Exception as e:
        st.error(f"Error during content generation: {e}")
        return "Failed to get response from Gemini."

# FIX APPLIED: Removed @st.cache_resource decorator
def delete_uploaded_file(_client: genai.Client, uploaded_file: types.File):
    """Deletes the file from the Gemini File API storage (recommended after use)."""
    try:
        # _client is used to avoid hashing the unhashable Client object
        _client.files.delete(name=uploaded_file.name)
        # st.toast is a Streamlit command, which is now safe because the function is not cached
        st.toast(f"Clean up complete. File {uploaded_file.name} deleted.")
    except Exception as e:
        st.warning(f"Failed to delete file {uploaded_file.name}. Error: {e}")