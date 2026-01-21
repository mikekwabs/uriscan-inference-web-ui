"""
Uriscan Inference Dashboard - Main Application
"""

import streamlit as st
import os
from utils.api_client import InferenceAPIClient
from pages.inference import show_inference_page
from pages.overview import show_overview_page
from pages.detail import show_detail_page


# Page configuration
st.set_page_config(
    page_title="Uriscan Inference Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)



# API Configuration
BACKEND_URL = os.getenv(
    "BACKEND_API_URL",
    "https://api.knoxxi.net/knoxxi-uriscan-inference"
)


# Initialize API client
@st.cache_resource
def get_api_client():
    """Get or create API client instance"""
    return InferenceAPIClient(BACKEND_URL)


def main():
    """Main application"""
    
    # Get API client
    api_client = get_api_client()
    
    # Sidebar - Navigation
    st.sidebar.title("🔬 Uriscan Dashboard")
    st.sidebar.markdown("---")
    
    # Initialize page in session state
    if 'page' not in st.session_state:
        st.session_state.page = "🔬 Run Inference"
    
    # Page selector
    page = st.sidebar.radio(
        "Navigation",
        ["🔬 Run Inference", "📊 Performance Overview", "🔍 Submission Detail"],
        index=["🔬 Run Inference", "📊 Performance Overview", "🔍 Submission Detail"].index(st.session_state.page)
    )
    
    # Update session state
    st.session_state.page = page
    
    st.sidebar.markdown("---")
    
    # API Health Status
    st.sidebar.subheader("API Status")
    
    health = api_client.health_check()
    
    if health.get('status') == 'healthy':
        st.sidebar.success("✅ API Connected")
        
        # Show component status
        components = health.get('components', {})
        
        models = components.get('models', {})
        st.sidebar.caption(f"Models: {models.get('loaded', 0)}/{models.get('total', 0)}")
        
        db = components.get('database', {})
        if db.get('status') == 'ok':
            st.sidebar.caption("Database: ✅ Connected")
        else:
            st.sidebar.caption("Database: ❌ Error")
    else:
        st.sidebar.error("❌ API Disconnected")
        st.sidebar.caption(f"URL: {BACKEND_URL}")
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Backend: `{BACKEND_URL}`")
    
    # Route to appropriate page
    if page == "🔬 Run Inference":
        show_inference_page(api_client)
    elif page == "📊 Performance Overview":
        show_overview_page(api_client)
    elif page == "🔍 Submission Detail":
        show_detail_page(api_client)


if __name__ == "__main__":
    main()