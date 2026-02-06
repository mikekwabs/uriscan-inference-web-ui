"""
Components for submission detail view
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from utils.formatting import (
    format_timestamp,
    format_percentage,
    get_agreement_badge,
    get_status_badge
)

def render_submission_summary(details: Dict[str, Any]):
    """
    Render overall submission summary card
    
    Args:
        details: Submission details dictionary
    """
    st.subheader("📋 Submission Summary")
    
    # Main metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Submission ID",
            details.get('submission_id', 'N/A')
        )
    
    with col2:
        agreement_pct = details.get('overall_agreement_pct', 0)
        st.metric(
            "Overall Agreement",
            format_percentage(agreement_pct),
            help="Percentage of models that agreed with ground truth"
        )
    
    with col3:
        correct = details.get('correct_predictions', 0)
        total = details.get('total_parameters', 0)
        st.metric(
            "Correct / Total",
            f"{correct} / {total}"
        )
    
    with col4:
        run_count = details.get('run_count', 1)
        st.metric(
            "Run Count",
            f"#{run_count}",
            help="Number of times inference has been run on this submission"
        )
    
    with col5:
        last_updated = details.get('last_updated') or details.get('inference_timestamp')
        st.metric(
            "Last Updated",
            format_timestamp(last_updated)
        )
    
    # Additional metadata if available
    if details.get('user_id') or details.get('lab_name'):
        st.markdown("---")
        
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        
        with meta_col1:
            if details.get('user_id'):
                st.caption(f"**User:** {details.get('user_id')}")
        
        with meta_col2:
            if details.get('lab_name'):
                st.caption(f"**Lab:** {details.get('lab_name')}")
        
        with meta_col3:
            if details.get('created_at'):
                st.caption(f"**First Run:** {format_timestamp(details.get('created_at'))}")


def render_statistics_breakdown(statistics: Dict[str, Any]):
    """
    Render statistics breakdown by model status
    
    Args:
        statistics: Statistics dictionary
    """
    st.subheader("📊 Performance by Model Status")
    
    if 'by_status' not in statistics:
        st.info("No status breakdown available")
        return
    
    by_status = statistics['by_status']
    
    col1, col2 = st.columns(2)
    
    # Production models
    with col1:
        st.markdown("#### 🟦 Production Models")
        
        prod = by_status.get('production', {})
        prod_total = prod.get('total', 0)
        prod_correct = prod.get('correct', 0)
        prod_agreement = prod.get('agreement_pct', 0)
        
        if prod_total > 0:
            st.metric(
                "Agreement",
                format_percentage(prod_agreement),
                delta=f"{prod_correct}/{prod_total} correct"
            )
            
            # Progress bar
            st.progress(prod_agreement / 100.0)
        else:
            st.info("No production models tested")
    
    # Shadow models
    with col2:
        st.markdown("#### 🟨 Shadow Models")
        
        shadow = by_status.get('shadow_mode', {})
        shadow_total = shadow.get('total', 0)
        shadow_correct = shadow.get('correct', 0)
        shadow_agreement = shadow.get('agreement_pct', 0)
        
        if shadow_total > 0:
            st.metric(
                "Agreement",
                format_percentage(shadow_agreement),
                delta=f"{shadow_correct}/{shadow_total} correct"
            )
            
            # Progress bar
            st.progress(shadow_agreement / 100.0)
        else:
            st.info("No shadow models tested")
    
    # Comparison
    if prod_total > 0 and shadow_total > 0:
        st.markdown("---")
        
        diff = shadow_agreement - prod_agreement
        
        if abs(diff) < 5:
            comparison = "📊 Production and Shadow models performing similarly"
        elif diff > 0:
            comparison = f"📈 Shadow models outperforming Production by {abs(diff):.1f}%"
        else:
            comparison = f"📉 Production models outperforming Shadow by {abs(diff):.1f}%"
        
        st.info(comparison)


def render_parameter_breakdown(parameters: List[Dict[str, Any]]):
    """
    Render detailed parameter-by-parameter breakdown table
    
    Args:
        parameters: List of parameter result dictionaries
    """
    st.subheader("🔬 Parameter Results")
    
    if not parameters:
        st.warning("No parameter results available")
        return
    
    # Prepare data
    table_data = []
    
    for param in parameters:
        agreement = param.get('agreement')
        agreement_pct = param.get('agreement_pct', 0)
        
        table_data.append({
            'Agreement': get_agreement_badge(agreement),
            'Parameter': param.get('parameter_name', 'N/A'),
            'Model Type': param.get('model_type', 'N/A'),
            'Prediction': param.get('prediction', 'N/A'),
            'Ground Truth': param.get('ground_truth_raw', 'N/A'),
            'GT Binary': param.get('ground_truth_binary', 'N/A'),
            'Agreement %': agreement_pct,
            'Probability': param.get('probability', 0),
            'Threshold': param.get('threshold', 0),
            # 'Confidence': param.get('confidence', 'N/A')
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Style function
    def highlight_disagreement(row):
        """Highlight rows where agreement is False"""
        if row['Agreement'] == '❌':
            return ['background-color: #f8d7da'] * len(row)
        else:
            return ['background-color: #d4edda'] * len(row)
    
    styled_df = df.style.apply(highlight_disagreement, axis=1).format({
        'Agreement %': '{:.1f}%',
        'Probability': '{:.4f}',
        'Threshold': '{:.2f}'
    })
    
    # Display table
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Summary counts
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    total = len(parameters)
    agreed = sum(1 for p in parameters if p.get('agreement') is True)
    disagreed = total - agreed
    
    with col1:
        st.metric("✅ Agreed", agreed)
    
    with col2:
        st.metric("❌ Disagreed", disagreed)
    
    with col3:
        st.metric("📊 Agreement Rate", f"{agreed/total*100:.1f}%" if total > 0 else "0%")


def render_disagreements_only(parameters: List[Dict[str, Any]]):
    """
    Render table showing only disagreements
    
    Args:
        parameters: List of parameter result dictionaries
    """
    disagreements = [p for p in parameters if p.get('agreement') is False]
    
    if not disagreements:
        st.success("🎉 Perfect! All parameters agreed with ground truth!")
        return
    
    st.warning(f"⚠️ {len(disagreements)} Disagreement(s) Found")
    
    # Show disagreements
    for param in disagreements:
        with st.expander(f"❌ {param.get('parameter_name', 'Unknown')} - {param.get('model_status', 'unknown')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Model Prediction:**")
                st.info(f"{param.get('prediction', 'N/A')} (prob: {param.get('probability', 0):.3f})")
            
            with col2:
                st.markdown("**Ground Truth:**")
                st.info(f"{param.get('ground_truth_binary', 'N/A')} (raw: {param.get('ground_truth_raw', 'N/A')})")
            
            # st.caption(f"Model: {param.get('model_type', 'N/A').upper()} | "
            #           f"Threshold: {param.get('threshold', 0):.2f} | "
            #           f"Confidence: {param.get('confidence', 'N/A')}"
            #           )