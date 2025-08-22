import os

# Global variable to store the API key
OPENAI_API_KEY = None

def get_openai_api_key():
    """Get OpenAI API key with lazy loading - prioritizes user input"""
    global OPENAI_API_KEY
    
    # First, check if user provided an API key in the UI
    try:
        import streamlit as st
        user_key = st.session_state.get('user_api_key', '')
        if user_key and user_key.strip():
            return user_key.strip()
    except (ImportError, AttributeError):
        pass
    
    # If no user key, check cached global key
    if OPENAI_API_KEY:
        return OPENAI_API_KEY
    
    # Try to get from Streamlit secrets
    try:
        import streamlit as st
        OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
        if OPENAI_API_KEY:
            return OPENAI_API_KEY
    except (ImportError, FileNotFoundError, KeyError, AttributeError):
        pass
    
    # Fallback to environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if OPENAI_API_KEY:
            return OPENAI_API_KEY
    except ImportError:
        pass
    
    # Check environment directly
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        return OPENAI_API_KEY
    
    # If still not found, raise error
    raise ValueError("OpenAI API key not found. Please provide your API key in the Settings panel or contact the administrator.")

# Don't load API key at import time - only when requested
# This prevents startup errors when the key isn't available yet

# File paths
SAMPLE_DATA_DIR = "Sample Data"
OUTPUT_DIR = "output"
TEMPLATES_DIR = "templates"

# Ensure directories exist (important for cloud deployment)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs("submissions", exist_ok=True)
