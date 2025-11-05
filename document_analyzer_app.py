import os
import streamlit as st
from pathlib import Path
from google import genai # type: ignore
from google.genai import types # type: ignore

# --- Gemini API Client Setup (SECURELY FETCHING KEY) ---

def initialize_client():
    """Initializes the Gemini client using the key from Streamlit Secrets."""
    
    if 'client' not in st.session_state:
        # 🔑 SECURE FIX: Read the API key from Streamlit Secrets
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except KeyError:
            st.session_state.client_error = (
                "🛑 GEMINI_API_KEY not found in Streamlit secrets. "
                "Please create a .streamlit/secrets.toml file and add your key."
            )
            st.session_state.client = None
            return None
        
        try:
            # Pass the retrieved API key explicitly to the Client constructor
            st.session_state.client = genai.Client(api_key=api_key)
        
        except Exception as e:
            # Store the error to display to the user later if initialization fails
            st.session_state.client_error = str(e)
            st.session_state.client = None
            
    return st.session_state.client

# --- Core Processing Functions (Unchanged from previous fix) ---

@st.cache_resource
def upload_document(_client: genai.Client, uploaded_file_obj) -> types.File:
    """
    Uploads the file object from Streamlit to the Gemini File API.
    NOTE: `_client` is underscored for Streamlit caching compatibility.
    """
    file_name = uploaded_file_obj.name
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / file_name

    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file_obj.getbuffer())

    st.info(f"Uploading file: {file_name} to Google File API...")
    try:
        uploaded_file = _client.files.upload(
            file=str(temp_file_path)
        )
        st.success(f"File uploaded successfully! Name: {uploaded_file.name}")
        return uploaded_file
    except Exception as e:
        st.error(f"Error during file upload: {e}")
        return None
    finally:
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

@st.cache_resource
def delete_uploaded_file(_client: genai.Client, uploaded_file: types.File):
    """Deletes the file from the Gemini File API storage (recommended after use)."""
    try:
        _client.files.delete(name=uploaded_file.name)
        st.toast(f"Clean up complete. File {uploaded_file.name} deleted.")
    except Exception as e:
        st.warning(f"Failed to delete file {uploaded_file.name}. Error: {e}")

# --- NEW CHAT FUNCTIONALITY (Unchanged) ---

def chat_with_document(client: genai.Client):
    """Handles the chat interaction with the uploaded document."""
    
    if 'uploaded_file_object' not in st.session_state or st.session_state.uploaded_file_object is None:
        st.info("Upload a document in the sidebar to begin chatting.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append(
            {"role": "assistant", "content": "Document analysis ready! Ask me any question about the content."}
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about the document..."):
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing content..."):
                file_obj = st.session_state.uploaded_file_object
                
                response = process_document(client, file_obj, prompt)
                
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# --- Streamlit UI Implementation (Unchanged) ---

def main():
    st.set_page_config(page_title="Gemini Document Analyzer", layout="wide")
    st.title("📄 AI Document Analyzer & Chat")
    st.markdown("Upload any document (PDF, TXT, DOCX, etc.) and chat with it.")
    st.divider()

    # 1. Initialize Client
    client = initialize_client()
    if client is None:
        st.error(
            "🛑 Gemini Client failed to initialize. Please check your API key setup."
        )
        if 'client_error' in st.session_state:
            st.code(st.session_state.client_error)
        return 

    # Initialize session state for the uploaded file object and cleanup status
    if 'uploaded_file_object' not in st.session_state:
        st.session_state.uploaded_file_object = None
    if 'cleanup_done' not in st.session_state:
        st.session_state.cleanup_done = False

    # 2. Sidebar Upload and Controls
    with st.sidebar:
        st.header("Upload Document")
        
        uploaded_file_input = st.file_uploader(
            "Choose a document file", 
            type=['pdf', 'txt', 'docx', 'pptx', 'md'],
            accept_multiple_files=False,
            key="file_uploader"
        )
        
        if st.session_state.uploaded_file_object and uploaded_file_input is None:
             st.warning("File is loaded. To upload a new file, clear the current one.")

        if uploaded_file_input and st.sidebar.button("Process Document", use_container_width=True, type="primary"):
            if st.session_state.uploaded_file_object:
                delete_uploaded_file(client, st.session_state.uploaded_file_object)
            
            with st.spinner(f"Processing {uploaded_file_input.name}..."):
                file_obj = upload_document(client, uploaded_file_input)
                
                if file_obj:
                    st.session_state.uploaded_file_object = file_obj
                    st.session_state.messages = []
                    st.session_state.cleanup_done = False
                    st.rerun()

        st.divider()
        st.markdown(
            "**Note on Cleanup:** The file will be deleted from storage when you close the application or upload a new file."
        )
        
        if st.session_state.uploaded_file_object and not st.session_state.cleanup_done:
             if st.button("Manually Delete File from API", use_container_width=True):
                 delete_uploaded_file(client, st.session_state.uploaded_file_object)
                 st.session_state.uploaded_file_object = None
                 st.session_state.cleanup_done = True
                 st.session_state.messages = []
                 st.rerun()


    # 3. Chat Interface
    chat_with_document(client)

if __name__ == "__main__":
    main()