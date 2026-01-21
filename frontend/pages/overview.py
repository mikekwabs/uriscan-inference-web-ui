"""
Performance Overview page - High-level submission tracking
"""

import streamlit as st
from utils.api_client import InferenceAPIClient
from components.filters import (
    render_date_range_filter,
    render_agreement_filter,
    render_search_filter,
    render_sort_options
)
from components.tables import (
    render_submissions_table,
    render_pagination_controls
)
from components.stats import render_summary_stats


def show_overview_page(api_client: InferenceAPIClient):
    """
    Display the performance overview page
    
    Args:
        api_client: API client instance
    """
    st.title("📊 Performance Overview")
    st.markdown("Track model performance across all submissions")
    st.markdown("---")
    
    # Initialize session state for pagination
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    if 'page_size' not in st.session_state:
        st.session_state.page_size = 50
    
    # Layout: Filters sidebar and main content
    col_filters, col_main = st.columns([1, 3])
    
    # Filters section
    with col_filters:
        st.markdown("### 🎛️ Filters")
        
        # Date range filter
        start_date, end_date = render_date_range_filter()
        
        st.markdown("---")
        
        # Agreement filter
        min_agreement = render_agreement_filter()
        
        st.markdown("---")
        
        # Search filter
        search_query = render_search_filter()
        
        st.markdown("---")
        
        # Sort options
        sort_by, sort_order = render_sort_options()
        
        st.markdown("---")
        
        # Apply button
        apply_filters = st.button("🔍 Apply Filters", type="primary", use_container_width=True)
        
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.current_page = 1
            st.rerun()
    
    # Main content section
    with col_main:
        # Fetch data
        with st.spinner("Loading submissions..."):
            try:
                # Calculate offset
                offset = (st.session_state.current_page - 1) * st.session_state.page_size
                
                # Call API
                response = api_client.get_submissions(
                    limit=st.session_state.page_size,
                    offset=offset,
                    min_agreement=min_agreement,
                    start_date=start_date,
                    end_date=end_date,
                    sort_by=sort_by,
                    sort_order=sort_order
                )
                
                submissions = response.get('submissions', [])
                pagination = response.get('pagination', {})
                
                # Filter by search query (client-side for now)
                if search_query:
                    submissions = [
                        s for s in submissions 
                        if search_query.lower() in s.get('submission_id', '').lower()
                    ]
                
                # Summary statistics
                if submissions:
                    render_summary_stats(submissions)
                    st.markdown("---")
                
                # Submissions table
                st.subheader(f"Submissions ({pagination.get('total_count', 0)})")
                render_submissions_table(submissions)
                
                # Pagination controls
                def handle_page_change(new_page, new_page_size=None):
                    st.session_state.current_page = new_page
                    if new_page_size:
                        st.session_state.page_size = new_page_size
                        st.session_state.current_page = 1  # Reset to first page when changing size
                    st.rerun()
                
                if pagination.get('total_count', 0) > 0:
                    render_pagination_controls(pagination, handle_page_change)
                
                # Export option
                if submissions:
                    st.markdown("---")
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        if st.button("📥 Export to CSV", use_container_width=True):
                            import pandas as pd
                            
                            # Prepare export data
                            export_data = []
                            for sub in submissions:
                                export_data.append({
                                    'Submission ID': sub.get('submission_id'),
                                    'Timestamp': sub.get('inference_timestamp'),
                                    'Total Parameters': sub.get('total_parameters'),
                                    'Correct Predictions': sub.get('correct_predictions'),
                                    'Agreement %': sub.get('overall_agreement_pct')
                                })
                            
                            df = pd.DataFrame(export_data)
                            csv = df.to_csv(index=False)
                            
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name=f"submissions_export_{st.session_state.current_page}.csv",
                                mime="text/csv"
                            )
                    
                    with col2:
                        if st.button("🔄 Refresh Data", use_container_width=True):
                            st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error loading submissions: {str(e)}")
                st.exception(e)