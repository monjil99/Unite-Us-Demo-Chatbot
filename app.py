import streamlit as st
import os
from admin_interface import show_admin_interface
from client_interface import show_client_interface
from auth import show_login_page, is_authenticated, get_interface_type
import config

# Configure Streamlit page
st.set_page_config(
    page_title="Interactive Intake Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    
    .interface-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
        background: #f9f9f9;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        margin-right: 2rem;
    }
    
    .progress-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sidebar .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Check authentication first
    if not is_authenticated():
        show_login_page()
        return
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Interactive Intake Chatbot System</h1>
        <p>Streamlined assistance request forms with AI-powered conversation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get selected interface from login
    interface_type = get_interface_type()
    
    # Show interface info in sidebar
    st.sidebar.title("🚀 Current Interface")
    if interface_type == "client":
        st.sidebar.success("👤 **Client Portal**")
        st.sidebar.markdown("""
        ### Features:
        - Interactive chatbot conversation
        - Step-by-step guidance
        - Real-time validation and suggestions
        - FAQ support
        - Progress tracking
        """)
    else:
        st.sidebar.success("🏢 **Admin Portal**")
        st.sidebar.markdown("""
        ### Features:
        - Create and edit form templates
        - Manage questions and responses
        - Preview forms
        - Export data
        - Multi-organization support
        """)
    
    # Add system status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Status")
    
    # Check if templates are loaded
    try:
        from data_models import DataManager
        from auth import get_user_templates, get_user_info
        dm = DataManager()
        all_templates = dm.get_all_templates()
        user_templates = get_user_templates()
        accessible_templates = {k: v for k, v in all_templates.items() if k in user_templates}
        
        user_info = get_user_info()
        st.sidebar.success(f"✅ {len(accessible_templates)} form templates available")
        st.sidebar.info(f"**Organization:** {user_info['business_name']}")
        
        # Show accessible template names
        if accessible_templates:
            st.sidebar.markdown("**Your Forms:**")
            for key, template in accessible_templates.items():
                st.sidebar.markdown(f"• {template.name}")
    except Exception as e:
        st.sidebar.error(f"❌ Error loading templates: {e}")
    
    # Check OpenAI connection
    try:
        import openai
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        st.sidebar.success("✅ OpenAI connection ready")
    except Exception as e:
        st.sidebar.error(f"❌ OpenAI error: {e}")
    
    # Main content area
    st.markdown("---")
    
    if interface_type == "client":
        show_client_interface()
    else:
        show_admin_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p>🤖 Interactive Intake Chatbot System | Powered by OpenAI GPT-4o Mini & Streamlit</p>
        <p>Built for streamlined social services intake and assistance request processing</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
