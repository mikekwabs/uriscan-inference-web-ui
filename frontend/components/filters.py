"""
Reusable filter components for the dashboard
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Optional


def render_date_range_filter() -> Tuple[Optional[str], Optional[str]]:
    """
    Render date range filter
    
    Returns:
        Tuple of (start_date, end_date) in ISO format, or (None, None)
    """
    st.subheader("📅 Date Range")
    
    # Preset options
    preset = st.selectbox(
        "Quick Select",
        ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Custom Range"],
        label_visibility="collapsed"
    )
    
    start_date = None
    end_date = None
    
    if preset == "Today":
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    elif preset == "Last 7 Days":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
    
    elif preset == "Last 30 Days":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    
    elif preset == "Custom Range":
        col1, col2 = st.columns(2)
        
        with col1:
            start_input = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
            if start_input:
                start_date = datetime.combine(start_input, datetime.min.time())
        
        with col2:
            end_input = st.date_input("End Date", value=datetime.now())
            if end_input:
                end_date = datetime.combine(end_input, datetime.max.time())
    
    # Convert to ISO format strings
    start_str = start_date.isoformat() if start_date else None
    end_str = end_date.isoformat() if end_date else None
    
    return start_str, end_str


def render_agreement_filter() -> Optional[float]:
    """
    Render minimum agreement percentage filter
    
    Returns:
        Minimum agreement percentage (0-100) or None
    """
    st.subheader("📊 Agreement Filter")
    
    use_filter = st.checkbox("Filter by minimum agreement", value=False)
    
    if use_filter:
        min_agreement = st.slider(
            "Minimum Agreement %",
            min_value=0,
            max_value=100,
            value=70,
            step=5,
            help="Show only submissions with agreement >= this percentage"
        )
        return float(min_agreement)
    
    return None


def render_search_filter() -> str:
    """
    Render submission ID search filter
    
    Returns:
        Search query string
    """
    st.subheader("🔍 Search")
    
    search_query = st.text_input(
        "Submission ID",
        placeholder="Search by submission ID...",
        label_visibility="collapsed"
    )
    
    return search_query.strip()


def render_sort_options() -> Tuple[str, str]:
    """
    Render sort options
    
    Returns:
        Tuple of (sort_by, sort_order)
    """
    st.subheader("🔄 Sort By")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sort_by = st.selectbox(
            "Field",
            ["timestamp", "agreement", "submission_id"],
            format_func=lambda x: {
                "timestamp": "Date/Time",
                "agreement": "Agreement %",
                "submission_id": "Submission ID"
            }[x],
            label_visibility="collapsed"
        )
    
    with col2:
        sort_order = st.selectbox(
            "Order",
            ["desc", "asc"],
            format_func=lambda x: "Newest First" if x == "desc" else "Oldest First",
            label_visibility="collapsed"
        )
    
    return sort_by, sort_order