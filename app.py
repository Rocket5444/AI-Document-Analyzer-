# app.py

import streamlit as st
# Import all logic functions from the engine.py file
from engine import (
    initialize_client, 
    upload_document, 
    process_document, 
    delete_uploaded_file
)

# --- NEW CHAT FUNCTIONALITY (UI) ---

def chat_with_document(client):
    """Handles the chat interaction with the uploaded document."""
    
    if 'uploaded_file_object' not in st.session_state or st.session_state.uploaded_file_object is None:
        st.info("Upload a document in the sidebar to begin chatting.")
        return

    # Initialize chat history if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append(
            {"role": "assistant", "content": "Document analysis ready! Ask me any question about the content."}
        )

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask a question about the document..."):
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing content..."):
                file_obj = st.session_state.uploaded_file_object
                
                # CALL BACKEND LOGIC
                response = process_document(client, file_obj, prompt)
                
                st.markdown(response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})


# --- Streamlit UI Implementation ---

def main():
    st.set_page_config(page_title="Gemini Document Analyzer", layout="wide")
    st.title("📄 AI Document Analyzer & Chat")
    st.markdown("Upload any document (PDF, TXT, DOCX, etc.) and chat with it.")
    st.divider()

    # 1. Initialize Client (Calling the backend)
    # The initialize_client returns the client object AND an error message (if any)
    client, error_message = initialize_client()
    
    if client is None:
        st.error("🛑 Client failed to initialize. " + error_message)
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
            # Clean up the previous file if one exists
            if st.session_state.uploaded_file_object:
                delete_uploaded_file(client, st.session_state.uploaded_file_object)
            
            with st.spinner(f"Processing {uploaded_file_input.name}..."):
                # CALL BACKEND LOGIC
                file_obj = upload_document(client, uploaded_file_input)
                
                if file_obj:
                    # Store the File object reference for chat access
                    st.session_state.uploaded_file_object = file_obj
                    # Reset UI state
                    st.session_state.messages = []
                    st.session_state.cleanup_done = False
                    st.rerun()

        st.divider()
        st.markdown(
            "**Note on Cleanup:** The file will be deleted from storage when you close the application or upload a new file."
        )
        
        if st.session_state.uploaded_file_object and not st.session_state.cleanup_done:
             if st.button("Manually Delete File from API", use_container_width=True):
                 # CALL BACKEND LOGIC
                 delete_uploaded_file(client, st.session_state.uploaded_file_object)
                 # Reset UI state
                 st.session_state.uploaded_file_object = None
                 st.session_state.cleanup_done = True
                 st.session_state.messages = []
                 st.rerun()


    # 3. Chat Interface
    chat_with_document(client)

if __name__ == "__main__":
    main()