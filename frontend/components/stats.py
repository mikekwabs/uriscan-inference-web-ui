"""
Statistics card components
"""

import streamlit as st
from typing import List, Dict, Any


def render_summary_stats(submissions: List[Dict[str, Any]]):
    """
    Render summary statistics cards
    
    Args:
        submissions: List of submission dictionaries
    """
    if not submissions:
        return
    
    # Calculate stats
    total = len(submissions)
    
    agreements = [s.get('overall_agreement_pct', 0) for s in submissions]
    avg_agreement = sum(agreements) / total if total > 0 else 0
    
    best_agreement = max(agreements) if agreements else 0
    worst_agreement = min(agreements) if agreements else 0
    
    high_performers = sum(1 for a in agreements if a >= 80)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Submissions",
            total,
            help="Total number of submissions in current view"
        )
    
    with col2:
        st.metric(
            "Avg Agreement",
            f"{avg_agreement:.1f}%",
            help="Average agreement percentage across all submissions"
        )
    
    with col3:
        st.metric(
            "High Performers",
            f"{high_performers}",
            delta=f"{high_performers/total*100:.0f}%" if total > 0 else "0%",
            help="Submissions with ≥80% agreement"
        )
    
    with col4:
        st.metric(
            "Range of Agreement",
            f"{worst_agreement:.0f}% - {best_agreement:.0f}%",
            help="Min to Max agreement percentage"
        )