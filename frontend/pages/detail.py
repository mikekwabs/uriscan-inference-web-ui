"""
Submission Detail page - Low-level parameter breakdown
"""

import streamlit as st
from utils.api_client import InferenceAPIClient
from components.detail_view import (
    render_submission_summary,
    render_statistics_breakdown,
    render_parameter_breakdown,
    render_disagreements_only
)


def show_detail_page(api_client: InferenceAPIClient):
    """
    Display the submission detail page
    
    Args:
        api_client: API client instance
    """
    st.title("🔍 Submission Detail")
    st.markdown("Detailed parameter-level breakdown for a specific submission")
    st.markdown("---")
    
    # Check if submission was selected from overview
    selected_from_overview = st.session_state.get('selected_submission_id')
    
    # Submission ID input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        submission_id = st.text_input(
            "Submission ID",
            value=selected_from_overview if selected_from_overview else "",
            placeholder="Enter submission ID or select from Performance Overview",
            help="Enter the submission ID to view detailed breakdown"
        )
    
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        load_button = st.button("📥 Load Details", type="primary", use_container_width=True)
        
        # Auto-load if coming from overview
        if selected_from_overview and not load_button:
            load_button = True
    
    # Load and display details
    if load_button or selected_from_overview:
        if not submission_id or not submission_id.strip():
            st.error("❌ Please enter a submission ID")
        else:
            with st.spinner(f"Loading details for {submission_id}..."):
                try:
                    # Fetch details from API
                    details = api_client.get_submission_detail(submission_id.strip())
                    
                    # Clear the selected submission from session state
                    if 'selected_submission_id' in st.session_state:
                        del st.session_state.selected_submission_id
                    
                    # Store in session state
                    st.session_state.current_detail = details
                    
                    st.success(f"✅ Loaded details for {submission_id}")
                    
                except ValueError as e:
                    st.error(f"❌ {str(e)}")
                    st.info("💡 This submission may not have been tracked yet. Try running inference on it first.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display details if available
    if 'current_detail' in st.session_state:
        details = st.session_state.current_detail
        
        st.markdown("---")
        
        # Summary card
        render_submission_summary(details)
        
        st.markdown("---")
        
        # # Statistics breakdown
        # if 'statistics' in details:
        #     render_statistics_breakdown(details['statistics'])
            
        #     st.markdown("---")
        
        # Tab view for different perspectives
        tab1, tab2 = st.tabs(["📋 All Parameters", "⚠️ Disagreements Only"])
        
        with tab1:
            # Full parameter breakdown
            parameters = details.get('parameters', [])
            render_parameter_breakdown(parameters)
        
        with tab2:
            # Disagreements only
            parameters = details.get('parameters', [])
            render_disagreements_only(parameters)
        
        # Action buttons
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Back to Overview", use_container_width=True):
                st.session_state.page = "📊 Performance Overview"
                st.rerun()
        
        with col2:
            if st.button("🔬 Run New Inference", use_container_width=True):
                st.session_state.page = "🔬 Run Inference"
                st.rerun()
        
        with col3:
            # Export button
            if st.button("📥 Export Details", use_container_width=True):
                import pandas as pd
                import json
                
                # Prepare export data
                export_data = []
                
                for param in details.get('parameters', []):
                    export_data.append({
                        'Submission ID': details.get('submission_id'),
                        'Parameter': param.get('parameter_name'),
                        'Model Status': param.get('model_status'),
                        'Model Type': param.get('model_type'),
                        'Prediction': param.get('prediction'),
                        'Ground Truth Raw': param.get('ground_truth_raw'),
                        'Ground Truth Binary': param.get('ground_truth_binary'),
                        'Agreement': param.get('agreement'),
                        'Probability': param.get('probability'),
                        'Threshold': param.get('threshold'),
                        # 'Confidence': param.get('confidence')
                    })
                
                df = pd.DataFrame(export_data)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{details.get('submission_id')}_detail.csv",
                    mime="text/csv"
                )
    
    else:
        # Show instructions if no data loaded
        st.info("""
        ### How to view submission details:
        
        1. **From Performance Overview:** Click on any submission ID in the overview table
        2. **Direct Entry:** Enter a submission ID above and click "Load Details"
        3. **After Inference:** Run inference on a submission, then view its details here
        
        The detail view shows:
        - Overall submission summary with agreement percentage
        - Breakdown by model status (Production vs Shadow)
        - Complete parameter-by-parameter results
        - Highlighted disagreements for easy identification
        """)
        
        # Quick link to overview
        if st.button("📊 Go to Performance Overview"):
            st.session_state.page = "📊 Performance Overview"
            st.rerun()