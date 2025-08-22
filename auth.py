"""
Authentication system for the Intake Chatbot
"""
import streamlit as st
from typing import Dict, List, Optional

# Business user mappings
BUSINESS_USERS = {
    "broomfield_admin": {
        "password": "123456",
        "business_name": "Broomfield Department of Health",
        "templates": ["broomfield"],
        "display_name": "Broomfield Health Admin"
    },
    "first_things_admin": {
        "password": "123456", 
        "business_name": "First Things First - Dads/Moms",
        "templates": ["first_things_first"],
        "display_name": "First Things First Admin"
    },
    "gateway_admin": {
        "password": "123456",
        "business_name": "Gateway YMCA Community Health", 
        "templates": ["gateway_ymca"],
        "display_name": "Gateway YMCA Admin"
    },
    "sbnj_admin": {
        "password": "123456",
        "business_name": "SBNJ Mobile Midwife Clinic",
        "templates": ["sbnj_mobile"],
        "display_name": "SBNJ Clinic Admin"
    }
}

def show_login_page():
    """Display the login page with interface selection"""
    st.title("🔐 Business Portal Login")
    st.markdown("---")
    
    # Interface selection first
    st.subheader("🚀 Select Your Interface")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("""
            <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; text-align: center; margin: 10px;">
                <h3>👤 Client Portal</h3>
                <p>Complete intake forms with interactive chatbot assistance</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🤖 Login as Client", use_container_width=True, type="primary"):
                st.session_state.selected_interface = "client"
                st.rerun()
    
    with col2:
        with st.container():
            st.markdown("""
            <div style="border: 2px solid #2196F3; border-radius: 10px; padding: 20px; text-align: center; margin: 10px;">
                <h3>🏢 Admin Portal</h3>
                <p>Manage forms, create templates, and configure questions</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("⚙️ Login as Admin", use_container_width=True):
                st.session_state.selected_interface = "admin"
                st.rerun()
    
    # Show login form if interface is selected
    if hasattr(st.session_state, 'selected_interface'):
        st.markdown("---")
        interface_type = st.session_state.selected_interface
        
        if interface_type == "client":
            st.subheader("👤 Client Login")
            st.info("Login to complete intake forms with our interactive chatbot assistant")
        else:
            st.subheader("🏢 Admin Login")
            st.info("Login to manage forms and create templates for your organization")
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your business username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_button:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.user_info = BUSINESS_USERS[username]
                    st.session_state.interface_type = interface_type
                    st.success(f"Welcome, {BUSINESS_USERS[username]['display_name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        
        # Back button
        if st.button("← Back to Interface Selection"):
            if 'selected_interface' in st.session_state:
                del st.session_state.selected_interface
            st.rerun()
    
    # Show available usernames for demo
    st.markdown("---")
    with st.expander("🔍 Demo Accounts (Click to see available usernames)"):
        st.markdown("**Available Business Accounts:**")
        for username, info in BUSINESS_USERS.items():
            st.markdown(f"• **{username}** - {info['display_name']}")
        st.markdown("**Password for all accounts:** `123456`")

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user"""
    if username in BUSINESS_USERS:
        return BUSINESS_USERS[username]["password"] == password
    return False

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def get_current_user() -> Optional[str]:
    """Get current logged-in user"""
    return st.session_state.get('current_user')

def get_user_info() -> Optional[Dict]:
    """Get current user information"""
    return st.session_state.get('user_info')

def get_user_templates() -> List[str]:
    """Get templates accessible to current user"""
    user_info = get_user_info()
    if user_info:
        return user_info.get('templates', [])
    return []

def get_interface_type() -> Optional[str]:
    """Get selected interface type (admin or client)"""
    return st.session_state.get('interface_type')

def logout():
    """Logout current user"""
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    if 'current_user' in st.session_state:
        del st.session_state.current_user
    if 'user_info' in st.session_state:
        del st.session_state.user_info
    if 'interface_type' in st.session_state:
        del st.session_state.interface_type
    if 'selected_interface' in st.session_state:
        del st.session_state.selected_interface
    if 'admin_page' in st.session_state:
        del st.session_state.admin_page
    if 'selected_template' in st.session_state:
        del st.session_state.selected_template
    st.rerun()

def show_user_header():
    """Show logged-in user header with logout option"""
    user_info = get_user_info()
    if user_info:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"👋 **Welcome, {user_info['display_name']}**")
            st.caption(f"Organization: {user_info['business_name']}")
        with col2:
            if st.button("🚪 Logout", key="logout_btn"):
                logout()
