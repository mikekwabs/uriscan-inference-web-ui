"""
Inference page - Run inference on submissions
"""

import streamlit as st
from utils.api_client import InferenceAPIClient
from utils.formatting import get_agreement_badge
import pandas as pd
from datetime import datetime, timezone


def format_submission_option(submission: dict) -> str:
    """
    Format submission for display in dropdown.

    Output example:
    Jan 20, 2026 — 06:58 PM UTC
    """
    sub_id = submission.get("id", "Unknown")

    # Support both snake_case and camelCase
    raw_ts =  submission.get("created_at")

    # Truncate long IDs
    display_id = (sub_id[:8] + "...") if isinstance(sub_id, str) and len(sub_id) > 12 else str(sub_id)

    ts_display = "Unknown time"
    if isinstance(raw_ts, str):
        try:
            # Parse ISO timestamp
            dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))

            # Force UTC
            dt = dt.astimezone(timezone.utc)

            # Format: Jan 20, 2026 — 06:58 PM UTC
            ts_display = dt.strftime("%b %d, %Y — %I:%M %p UTC")
        except Exception:
            pass

    return f"{display_id} - {ts_display}"


def show_inference_page(api_client: InferenceAPIClient):
    """
    Display the inference page
    
    Args:
        api_client: API client instance
    """
    st.title("🔬 Run Inference")
    st.markdown("Select a recent submission to run inference")
    st.markdown("---")
    
    # Input section
    st.subheader("📋 Select Submission")
    
    # Fetch recent submissions
    if 'recent_submissions' not in st.session_state:
        st.session_state.recent_submissions = []
        st.session_state.recent_submissions_loading = True
    
    # Load recent submissions
    if st.session_state.get('recent_submissions_loading', False):
        with st.spinner("Loading recent submissions..."):
            try:
                submissions = api_client.get_recent_submissions_from_knoxxi(limit=100)
                st.session_state.recent_submissions = submissions
                st.session_state.recent_submissions_loading = False
                st.session_state.last_refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Could not load recent submissions: {str(e)}")
                st.session_state.recent_submissions = []
                st.session_state.recent_submissions_loading = False
    
    recent_submissions = st.session_state.get('recent_submissions', [])
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if recent_submissions:
            # Create options with formatting
            options = [None] + recent_submissions
            
            selected = st.selectbox(
                "Recent Submissions",
                options=options,
                format_func=lambda x: "-- Select a submission --" if x is None else format_submission_option(x),
                help="Select from recently accepted submissions"
            )
            
            # Extract submission ID
            submission_id = selected.get('id', '') if selected else ''
            
            # Show count
            st.caption(f"📊 Showing {len(recent_submissions)} most recent submissions")
            
            if st.session_state.get('last_refresh_time'):
                st.caption(f"🕐 Last refreshed: {st.session_state.last_refresh_time}")
            
        else:
            st.warning("⚠️ No recent submissions available")
            submission_id = ''
    
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        
        run_button = st.button(
            "🚀 Run Inference", 
            type="primary", 
            use_container_width=True,
            disabled=not submission_id
        )
        
    
    # Run inference
    if run_button:
        if not submission_id or not submission_id.strip():
            st.error("❌ Please select a submission")
        else:
            with st.spinner(f"Running inference on {submission_id}..."):
                try:
                    # Call API
                    result = api_client.run_inference(submission_id.strip())
                    
                    # Store in session state
                    st.session_state.last_inference_result = result
                    st.session_state.last_submission_id = submission_id.strip()
                    
                    st.success(f"✅ Inference completed for {submission_id}")
                    
                except ValueError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display results if available
    if 'last_inference_result' in st.session_state:
        result = st.session_state.last_inference_result
        
        st.markdown("---")
        st.subheader("Inference Results")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Submission ID",
                result.get('submission_id', 'N/A')
            )
        
        with col2:
            st.metric(
                "Total Parameters",
                result.get('total_parameters', 0)
            )
        
        with col3:
            successful = result.get('successful', 0)
            total = result.get('total_parameters', 0)
            st.metric(
                "Successful",
                f"{successful}/{total}"
            )
        
        with col4:
            failed = result.get('failed', 0)
            st.metric(
                "Failed",
                failed,
                delta=f"-{failed}" if failed > 0 else None,
                delta_color="inverse"
            )
        
        # Parameters table
        if 'parameters' in result and result['parameters']:
            st.markdown("### Parameter Results")
            
            # Prepare data for display
            params_data = []
            for param in result['parameters']:
                if param.get('status') == 'success':
                    params_data.append({
                        'Parameter': param.get('name', 'N/A'),
                        'Model': param.get('model_type', 'N/A').upper(),
                        'Prediction': param.get('prediction', 'N/A'),
                        'Ground Truth': param.get('ground_truth_raw', 'N/A'),
                        'Agreement': get_agreement_badge(param.get('agreement', False)),
                        'Probability': f"{param.get('probability', 0):.3f}",
                        # 'Confidence': param.get('confidence', 'N/A')
                    })
                else:
                    params_data.append({
                        'Parameter': param.get('name', 'N/A'),
                        'Model': '-',
                        'Prediction': '-',
                        'Ground Truth': '-',
                        'Agreement': '-',
                        'Probability': '-',
                        # 'Confidence': '-'
                    })
            
            # Display as dataframe
            df = pd.DataFrame(params_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Tracking info
            # if 'tracking' in result:
            #     tracking = result['tracking']
            #     if tracking.get('logged'):
            #         st.info(f"💾 {tracking.get('message', 'Results saved to database')}")
            #     else:
            #         st.warning(f"⚠️ {tracking.get('message', 'Results not saved to database')}")
        
        # Action buttons
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 View in Performance Overview", use_container_width=True):
                st.session_state.page = "📊 Performance Overview"
                st.rerun()
        
        with col2:
            if st.button("🔍 View Detailed Breakdown", use_container_width=True):
                st.session_state.selected_submission_id = result.get('submission_id')
                st.session_state.page = "🔍 Submission Detail"
                st.rerun()


def get_status_badge(status: str) -> str:
    """
    Get badge for model status
    
    Args:
        status: Model status (production/shadow_mode)
        
    Returns:
        Badge emoji
    """
    if status == "production":
        return "🟦"
    elif status == "shadow_mode":
        return "🟨"
    else:
        return "⬜"