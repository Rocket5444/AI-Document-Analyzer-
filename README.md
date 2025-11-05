# 📚 Gemini-Powered Document Analyzer & Chat App

This project is a web application built using **Streamlit** and the **Google GenAI SDK** that allows users to interact with large language models. While the core application currently provides a conversational chat interface, its foundation is designed to easily incorporate advanced features like uploading and analyzing documents (PDFs, images, etc.) using the Gemini API's powerful multimodal capabilities.

## ✨ Features

* **Secure API Key Management:** Utilizes Streamlit's `st.secrets` for securely handling your Gemini API key.

* **Real-time Chat:** Engages users in a stateful, multi-turn conversation powered by the `gemini-2.5-flash` model.

* **Scalable Architecture:** Built with Python for easy local development and one-click deployment to Streamlit Community Cloud.

* **Clear Dependency List:** Uses `requirements.txt` for hassle-free environment setup.

## 📂 Project File Structure

The project has the following key files and directories:

.├── .streamlit/             # Contains Streamlit configuration files (e.g., secrets.toml)

 ├── .venv/                  # Local Python Virtual Environment (ignored by Git)
 
 ├── app.py                  # The main Streamlit application file.
 
 ├── engine.py               # (Optional) Likely contains helper functions or complex logic.
 
 └── requirements.txt        # Lists all required Python packages for the project.
 
## ⚙️ Setup and Installation

Follow these steps to set up and run the application locally on your machine.

### 1. Clone the Repository

git clone <your-repository-url>cd <your-repository-name>
### 2. Create and Activate Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

Create the environmentpython -m venv .venvActivate the environment (Linux/macOS)source .venv/bin/activateActivate the environment (Windows)..venv\Scripts\activate
### 3. Install Dependencies

The required packages are listed in `requirements.txt`.

pip install -r requirements.txt
### 4. Set Up Your API Key (Crucial Step)

To connect to the Gemini API, you need an API key. This key must be stored securely using Streamlit's secrets management.

1. **Create the Secrets Folder:** In your project's root directory, create a hidden folder:

mkdir .streamlit
2. **Create the Secrets File:** Inside the `.streamlit` folder, create a file named `secrets.toml`:

touch .streamlit/secrets.toml
3. **Add Your Key:** Edit the `secrets.toml` file and paste your key in the following format:

.streamlit/secrets.tomlgemini_api_key = "YOUR_ACTUAL_API_KEY_HERE"
*Note: This `.streamlit/secrets.toml` file should be added to your `.gitignore` to prevent committing your key.*

## ▶️ How to Run Locally

Once the setup is complete, you can start the Streamlit application:

streamlit run app.py
The application will automatically open in your web browser, typically at `http://localhost:8501`.

## 🚀 Deployment to Streamlit Community Cloud

This app is ready for one-click deployment to the Streamlit Community Cloud.

1. **Commit and Push:** Ensure all your code (`app.py`, `requirements.txt`, etc., but **not** `secrets.toml`) is committed and pushed to your GitHub repository.

2. **Deploy:** Go to the [Streamlit Community Cloud](https://streamlit.io/cloud) and select "New app."

3. **Configure Repository:** Select your repository, branch (e.g., `main`), and the main file (`app.py`).

4. **Add Secrets:** In the **Advanced settings** section, paste the contents of your local `secrets.toml` file into the "Secrets" text area. **Do not include the `.streamlit/secrets.toml` file itself in your repository.**

   gemini_api_key = "YOUR_ACTUAL_API_KEY_HERE"
