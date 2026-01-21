"""
Reusable table components for the dashboard
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from utils.formatting import (
    format_timestamp, 
    get_agreement_indicator
)



def render_submissions_table(submissions: List[Dict[str, Any]]):
    """
    Render submissions table with clickable links
    
    Args:
        submissions: List of submission dictionaries
    """
    if not submissions:
        st.info("📭 No submissions found matching the filters")
        return
    
    # Prepare data for display
    table_data = []
    
    for sub in submissions:
        indicator = get_agreement_indicator(sub.get('overall_agreement_pct', 0))
        
        table_data.append({
            'Status': indicator,
            'Submission ID': sub.get('submission_id', 'N/A'),
            'Date/Time': format_timestamp(sub.get('inference_timestamp')),
            'Agreement %': sub.get('overall_agreement_pct', 0),
            'Correct': sub.get('correct_predictions', 0),
            'Total': sub.get('total_parameters', 0),
            'Models Tested': f"{sub.get('correct_predictions', 0)}/{sub.get('total_parameters', 0)}"
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Style the dataframe
    def style_agreement(val):
        """Color code agreement percentage"""
        if val >= 80:
            return 'background-color: #d4edda; color: #155724'
        elif val >= 50:
            return 'background-color: #fff3cd; color: #856404'
        else:
            return 'background-color: #f8d7da; color: #721c24'
    
    styled_df = df.style.map(
        style_agreement,
        subset=['Agreement %']
    ).format({
        'Agreement %': '{:.1f}%'
    })
    
    # Display table
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Make submission IDs clickable
    st.markdown("---")
    st.caption("💡 Click on a Submission ID below to view detailed breakdown")
    
    # Create buttons for each submission
    cols = st.columns(min(5, len(submissions)))
    
    for idx, sub in enumerate(submissions[:10]):  # Show first 10 clickable
        col_idx = idx % 5
        with cols[col_idx]:
            if st.button(
                sub.get('submission_id', 'N/A'),
                key=f"sub_btn_{sub.get('id')}",
                use_container_width=True
            ):
                # Store selected submission and navigate
                st.session_state.selected_submission_id = sub.get('submission_id')
                st.session_state.page = "🔍 Submission Detail"
                st.rerun()
    
    if len(submissions) > 10:
        st.caption(f"_Showing clickable links for first 10 submissions. Use search to find specific IDs._")





def render_pagination_controls(pagination: Dict[str, Any], on_page_change):
    """
    Render pagination controls
    
    Args:
        pagination: Pagination metadata from API
        on_page_change: Callback function for page changes
    """
    total_count = pagination.get('total_count', 0)
    current_page = pagination.get('current_page', 1)
    total_pages = pagination.get('total_pages', 1)
    has_next = pagination.get('has_next', False)
    has_prev = pagination.get('has_prev', False)
    
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 2])
    
    with col1:
        st.caption(f"**Total:** {total_count} submissions")
    
    with col2:
        if has_prev:
            if st.button("⬅️ Previous", use_container_width=True):
                on_page_change(current_page - 1)
        else:
            st.button("⬅️ Previous", disabled=True, use_container_width=True)
    
    with col3:
        st.caption(f"**Page {current_page} of {total_pages}**")
    
    with col4:
        if has_next:
            if st.button("Next ➡️", use_container_width=True):
                on_page_change(current_page + 1)
        else:
            st.button("Next ➡️", disabled=True, use_container_width=True)
    
    with col5:
        # Page size selector
        page_size = st.selectbox(
            "Per Page",
            [10, 25, 50, 100],
            index=2,  # Default 50
            key="page_size_selector"
        )
        
        if page_size != pagination.get('limit', 50):
            on_page_change(1, page_size)

