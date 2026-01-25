"""
Sidebar Styles - Extracted from home.py
Beautiful modern sidebar design with purple/pink gradients
Apply this to all pages for consistent styling
"""

import streamlit as st

def apply_sidebar_styles():
    """
    Apply the exact sidebar styling from home.py
    This creates the beautiful purple/pink gradient sidebar
    """
    st.markdown("""
    <style>
        /* SIDEBAR STYLING - Beautiful Modern Design */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1f3a 0%, #0f1419 100%);
            border-right: 1px solid rgba(139, 92, 246, 0.2);
        }
        
        /* Sidebar header */
        section[data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(236, 72, 153, 0.1) 100%);
            padding: 1.5rem 1rem;
            border-bottom: 2px solid rgba(139, 92, 246, 0.3);
        }
        
        /* Sidebar navigation items */
        section[data-testid="stSidebar"] .css-17lntkn,
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            padding-top: 2rem;
        }
        
        /* Sidebar nav links */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(236, 72, 153, 0.04) 100%);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 12px;
            margin: 0.3rem 0.5rem;
            padding: 0.75rem 1rem;
            color: #e2e8f0 !important;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(236, 72, 153, 0.08) 100%);
            border-color: rgba(139, 92, 246, 0.4);
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
        }
        
        /* Active/selected page in sidebar */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            border-color: rgba(255, 255, 255, 0.3);
            color: #ffffff !important;
            font-weight: 700;
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
        }
        
        /* Sidebar collapse button */
        section[data-testid="stSidebar"] button[kind="header"] {
            color: #8b5cf6;
        }
    </style>
    """, unsafe_allow_html=True)


def apply_page_styles():
    """
    Apply general page styling from home.py
    Dark theme, buttons, forms, etc.
    """
    st.markdown("""
    <style>
        /* Main dark gradient background */
        .main {
            background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        }
        
        /* Remove padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* header {visibility: hidden;} - Commented out to keep sidebar toggle visible */
        
        /* Headers */
        h1, h2, h3 {
            color: #ffffff !important;
            font-weight: 800 !important;
        }
        
        /* Form styling */
        .stForm {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(236, 72, 153, 0.05) 100%);
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%);
            color: white;
            font-weight: 700;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-size: 1rem;
            box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            box-shadow: 0 6px 30px rgba(139, 92, 246, 0.6);
            transform: translateY(-2px);
        }
        
        /* Selectbox and multiselect styling */
        .stSelectbox > div > div,
        .stMultiSelect > div > div {
            background: rgba(15, 20, 25, 0.6);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 8px;
            color: #ffffff;
        }
        
        /* Slider styling */
        .stSlider > div > div > div {
            background: linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%);
        }
        
        /* Info/success boxes */
        .stAlert {
            background: rgba(15, 20, 25, 0.6);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            color: #e2e8f0;
        }
        
        /* Text colors */
        p, label, .stMarkdown {
            color: #e2e8f0 !important;
        }
        
        /* Caption text */
        .css-16huue1 {
            color: #94a3b8 !important;
        }
    </style>
    """, unsafe_allow_html=True)


def apply_all_styles():
    """
    Apply both sidebar and page styles in one call
    Use this at the top of each page for complete styling
    """
    apply_sidebar_styles()
    apply_page_styles()