
import streamlit as st
from pathlib import Path

# Define the navigation order
# Format: Screen Name, File Path
NAV_PAGES = [
    ("Home", "home.py"),
    ("Dashboard", "pages/1_Dashboard.py"),
    ("Smart Search", "pages/2_Smart_Search.py"),
    ("Map Analysis", "pages/3_Map_Analysis.py"),
    ("Correlations", "pages/4_Correlations.py"),
    ("Income Simulator", "pages/5_Income_Simulator.py"),
    ("Data Quality", "pages/6_Data_Quality.py"),
    ("Sunburst", "pages/7_Sunburst.py"),
    ("Temporal Comparison", "pages/8_Temporal_Comparison.py"),
    ("Help", "pages/9_Help.py"),
]

def render_navigation_buttons():
    """
    Renders Previous/Next buttons at the bottom of the page
    to allow sequential navigation through the app.
    """
    try:
        current_source = st.get_option("server.runOnSave") # Just a dummy call to ensure st context, though not strictly needed for this logic.
        
        # We need to identify the current page.
        # Streamlit doesn't give a direct "current page file" API easily publicly, 
        # but we can infer it or pass it. 
        # However, passing it manually in every file is robust.
        # Let's try to detect it from the call stack or context, but manual passing is safer if I'm editing every file anyway.
        # Actually, let's just make the caller pass the current file name, or I can try to find it.
        pass
    except:
        pass

    # Re-impl with robust matching:
    # Since I am editing every file, I will just call render_bottom_nav(__file__)
    pass

def bottom_nav_layout(current_file_path):
    st.markdown("---")
    
    # Normalize paths for comparison
    # current_file_path will be absolute path on disk when passed from __file__
    # NAV_PAGES has relative paths.
    
    current_path = Path(current_file_path)
    current_name = current_path.name
    
    # Identify current index
    current_idx = -1
    for idx, (label, fname) in enumerate(NAV_PAGES):
        if Path(fname).name == current_name:
            current_idx = idx
            break
            
    if current_idx == -1:
        # Fallback for home.py if run directly not matching exactly or variations
        if "home.py" in current_name:
             current_idx = 0
    
    if current_idx == -1:
        return # Could not identify page
        
    cols = st.columns([1, 4, 1])
    
    # Previous Button
    with cols[0]:
        if current_idx > 0:
            prev_label, prev_file = NAV_PAGES[current_idx - 1]
            if st.button(f"← {prev_label}", use_container_width=True):
                st.switch_page(prev_file)
                
    # Next Button
    with cols[2]:
        if current_idx < len(NAV_PAGES) - 1:
            next_label, next_file = NAV_PAGES[current_idx + 1]
            if st.button(f"{next_label} →", use_container_width=True):
                st.switch_page(next_file)

