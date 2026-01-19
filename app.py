import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "https://api.knoxxi.net/knoxxi-uriscan-inference").rstrip('/')

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.36.0",
}

# Page config
st.set_page_config(
    page_title="Uriscan CNN Inference",
    page_icon="🧪",
    layout="wide"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'selected_submission_id' not in st.session_state:
    st.session_state.selected_submission_id = None

# ============================================================
# API Client Functions
# ============================================================

def get_recent_submissions(limit=10):
    """Fetch recent accepted submissions from backend"""
    try:
        response = requests.get(
            f"{BACKEND_API_URL}/api/v1/submissions/recent",
            params={"limit": limit},
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch submissions: {e}")
        return None

def run_inference(submission_id):
    """Run inference on a submission"""
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/api/v1/inference/{submission_id}",
            headers=HEADERS,
            timeout=60  # Inference might take time
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Inference failed: {e}")
        return None

def check_backend_health():
    """Check if backend is reachable"""
    try:
        response = requests.get(
            f"{BACKEND_API_URL}/api/v1/health", 
            headers=HEADERS,
            timeout=5
            )
        return response.status_code == 200
    except:
        return False

# ============================================================
# UI Helper Functions
# ============================================================

def format_submission_option(submission):
    """Format submission for dropdown display"""
    created_at = submission.get('created_at', 'Unknown')
    sub_id = submission.get('id', 'Unknown')
    # Truncate ID for readability
    short_id = sub_id[:8] + "..." if len(sub_id) > 8 else sub_id
    return f"{short_id} - {created_at}"

def highlight_agreement(row):
    """Color code rows based on agreement"""
    colors = []
    for col in row.index:
        if col == 'Agreement':
            if row[col] == '✅':
                colors.append('background-color: #d4edda')  # Light green
            elif row[col] == '❌':
                colors.append('background-color: #f8d7da')  # Light red
            elif row[col] == '⚠️':
                colors.append('background-color: #fff3cd')  # Light yellow
            elif row[col] == '🔴':
                colors.append('background-color: #f5c6cb')  # Error red
            else:
                colors.append('')
        else:
            colors.append('')
    return colors

def prepare_results_dataframe(results):
    """Convert API results to pandas DataFrame"""
    rows = []
    
    for param in results['parameters']:
        if param['status'] == 'error':
            row = {
                'Parameter': param['name'],
                'Status': 'Error',
                'Model Type': '-',
                'Prediction': '-',
                'Probability': '-',
                'Confidence': '-',
                'Ground Truth': '-',
                'GT Binary': '-',
                'Agreement': '🔴',
                'Error': param.get('error', 'Unknown error')
            }
        else:
            # Format agreement
            if param['agreement'] is True:
                agreement_icon = '✅'
            elif param['agreement'] is False:
                agreement_icon = '❌'
            else:
                agreement_icon = '⚠️'
            
            row = {
                'Parameter': param['name'],
                'Status': param.get('model_status', 'unknown'),
                'Model Type': param['model_type'].upper(),
                'Prediction': param['prediction'],
                'Probability': f"{param['probability']:.3f}",
                'Confidence': param['confidence'],
                'Ground Truth': param['ground_truth_raw'] or 'N/A',
                'GT Binary': param['ground_truth_binary'] or 'N/A',
                'Agreement': agreement_icon,
                'Error': '-'
            }
        
        rows.append(row)
    
    return pd.DataFrame(rows)

# ============================================================
# Main App
# ============================================================

# Header
st.title("🧪 Uriscan Model Inference Dashboard")
st.markdown("---")

# Check backend connectivity
if not check_backend_health():
    st.error(f"⚠️ Cannot connect to backend at {BACKEND_API_URL}")
    st.info("Please ensure the backend API is running.")
    st.stop()

# ============================================================
# Section 1: Submission Selector
# ============================================================

st.subheader("📋 Select Submission")

col1, col2 = st.columns([3, 1])

with col1:
    # Fetch submissions
    submissions_data = get_recent_submissions(limit=10)
    
    if submissions_data and submissions_data.get('submissions'):
        submissions = submissions_data['submissions']
        
        # Create options for dropdown
        submission_options = {
            format_submission_option(sub): sub['id'] 
            for sub in submissions
        }
        
        selected_display = st.selectbox(
            "Recent Accepted Submissions",
            options=list(submission_options.keys()),
            help="Select a submission to run inference"
        )
        
        # Store selected submission ID
        st.session_state.selected_submission_id = submission_options[selected_display]
        
        st.caption(f"**Submission ID:** `{st.session_state.selected_submission_id}`")
    else:
        st.warning("No submissions available")
        st.stop()

with col2:
    st.metric("Available", f"{len(submissions)}", "submissions")

st.markdown("---")

# ============================================================
# Section 2: Run Inference
# ============================================================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 Run Inference", type="primary", use_container_width=True):
        with st.spinner("Running inference on all models... This may take 10-30 seconds."):
            results = run_inference(st.session_state.selected_submission_id)
            
            if results:
                st.session_state.results = results
                st.success("✅ Inference completed!")
            else:
                st.error("❌ Inference failed. Check backend logs.")

st.markdown("---")

# ============================================================
# Section 3: Results Display
# ============================================================

if st.session_state.results:
    results = st.session_state.results
    
    # Summary Section
    st.subheader("📊 Results Summary")
    
    summary = results['summary']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Models", summary['total'])
    
    with col2:
        st.metric("Agreements", summary['agreements'], delta=f"{summary['agreement_rate']*100:.1f}%")
    
    with col3:
        st.metric("Disagreements", summary['disagreements'])
    
    with col4:
        st.metric("Errors", summary['errors'])
    
    # Additional info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Production Models:** {summary['production_models']}")
    with col2:
        st.info(f"**Shadow Models:** {summary['shadow_models']}")
    with col3:
        st.info(f"**No Ground Truth:** {summary['no_ground_truth']}")
    
    st.markdown("---")
    
    # Detailed Results Table
    st.subheader("🔬 Detailed Results")
    
    df = prepare_results_dataframe(results)
    
    # Apply styling
    styled_df = df.style.apply(highlight_agreement, axis=1)
    
    # Display table
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )
    
    # Legend
    st.caption("""
    **Legend:**  
    ✅ Agreement | ❌ Disagreement | ⚠️ No Ground Truth | 🔴 Error  
    **Status:** production = Production-ready | shadow_mode = Shadow mode testing
    """)
    
    # Expandable section for raw JSON
    with st.expander("🔍 View Raw JSON Response"):
        st.json(results)
    
    # Download results as CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name=f"inference_results_{st.session_state.selected_submission_id[:8]}.csv",
        mime="text/csv"
    )

else:
    # Empty state
    st.info("👆 Select a submission and click 'Run Inference' to see results")

# ============================================================
# Footer
# ============================================================

st.markdown("---")
st.caption(f"Connected to: `{BACKEND_API_URL}` | Uriscan CNN Inference v1.0")