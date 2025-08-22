import os

# OpenAI Configuration - for cloud deployment and local development
try:
    # Try to import streamlit for cloud deployment
    import streamlit as st
    # Try to get the API key from Streamlit secrets first
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise KeyError("OPENAI_API_KEY not found in secrets")
except (ImportError, FileNotFoundError, KeyError):
    # Fallback to environment variables for local development
    try:
        from dotenv import load_dotenv
        load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        # If still not found, raise an error for security
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found. Please add it to Streamlit secrets or environment variables.")
    except ImportError:
        # If python-dotenv is not available, check environment
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found. Please add it to Streamlit secrets or environment variables.")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Please add it to Streamlit secrets or environment variables.")

# File paths
SAMPLE_DATA_DIR = "Sample Data"
OUTPUT_DIR = "output"
TEMPLATES_DIR = "templates"

# Ensure directories exist (important for cloud deployment)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs("submissions", exist_ok=True)
