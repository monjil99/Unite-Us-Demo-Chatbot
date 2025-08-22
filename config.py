import os

# Global variable to store the API key
OPENAI_API_KEY = None

def get_openai_api_key():
    """Get OpenAI API key with lazy loading"""
    global OPENAI_API_KEY
    
    if OPENAI_API_KEY:
        return OPENAI_API_KEY
    
    # Try to get from Streamlit secrets first
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
    raise ValueError("OPENAI_API_KEY not found. Please add it to Streamlit secrets or environment variables.")

# For backward compatibility, try to load the key but don't fail on import
try:
    OPENAI_API_KEY = get_openai_api_key()
except ValueError:
    # API key will be loaded when first needed
    pass

# File paths
SAMPLE_DATA_DIR = "Sample Data"
OUTPUT_DIR = "output"
TEMPLATES_DIR = "templates"

# Ensure directories exist (important for cloud deployment)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs("submissions", exist_ok=True)
