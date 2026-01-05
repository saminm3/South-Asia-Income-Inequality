# utils/state.py
import streamlit as st

def get_analysis_config():
    """Return analysis_config dict or None."""
    return st.session_state.get("analysis_config")

def require_analysis_config():
    """Stop page if Home config is missing."""
    config = get_analysis_config()
    if not config:
        st.warning("⚠️ No analysis configured. Please configure your analysis on the Home page.")
        st.info("Click 'home' in the sidebar to configure your analysis")
        st.stop()
    return config
