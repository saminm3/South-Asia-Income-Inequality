"""
Simplified Contextual Help System - Streamlit Native
Uses expanders instead of JavaScript modals for better compatibility
"""

import streamlit as st

def render_help_button(page_name: str):
    """
    Renders a help section using Streamlit's native expander
    More reliable than JavaScript modals in Streamlit
    """
    
    # Import help content
    from .help_content import HELP_CONTENT
    
    # Get help content for this page
    help_data = HELP_CONTENT.get(page_name)
    
    if not help_data:
        return  # No help content defined for this page
    
    # CSS for help button styling
    st.markdown("""
    <style>
        /* Help section container */
        .help-section-container {
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 999;
            max-width: 400px;
        }
        
        /* Help expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            color: white !important;
            border-radius: 50px;
            font-weight: 600;
            padding: 12px 20px;
            box-shadow: 0 4px 20px rgba(139, 92, 246, 0.5);
        }
        
        .streamlit-expanderHeader:hover {
            box-shadow: 0 6px 30px rgba(139, 92, 246, 0.7);
            transform: scale(1.05);
        }
        
        /* Help content box */
        .help-content-box {
            background: linear-gradient(180deg, #1a1f3a 0%, #0f1419 100%);
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin-top: 10px;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .help-content-box h3 {
            color: #8b5cf6;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        
        .help-content-box ul {
            color: #e2e8f0;
            padding-left: 20px;
        }
        
        .help-content-box li {
            margin-bottom: 8px;
            line-height: 1.6;
        }
        
        .help-tip-box {
            background: rgba(139, 92, 246, 0.1);
            border-left: 4px solid #8b5cf6;
            padding: 12px;
            border-radius: 6px;
            margin: 12px 0;
            color: #e2e8f0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create help section
    with st.container():
        with st.expander("❓ Quick Help for This Page", expanded=False):
            st.markdown(f"""
            <div class='help-content-box'>
                <h2 style='color: #ffffff; margin-top: 0;'>{help_data['title']}</h2>
                <p style='color: #94a3b8;'>{help_data['overview']}</p>
            """, unsafe_allow_html=True)
            
            # Features
            if help_data.get('features'):
                st.markdown("### 📋 Key Features")
                for feature in help_data['features']:
                    st.markdown(f"**{feature['name']}** - {feature['description']}")
            
            # How to use
            if help_data.get('how_to_use'):
                st.markdown("###  How to Use")
                for i, step in enumerate(help_data['how_to_use'], 1):
                    st.markdown(f"{i}. {step}")
            
            # Tips
            if help_data.get('tips'):
                st.markdown("""
                <div class='help-tip-box'>
                    <strong>💡 Pro Tips:</strong>
                </div>
                """, unsafe_allow_html=True)
                for tip in help_data['tips']:
                    st.markdown(f"- {tip}")
            
            # Common issues
            if help_data.get('common_issues'):
                st.markdown("### ❓ Common Issues & Solutions")
                for issue in help_data['common_issues']:
                    st.markdown(f"**{issue['problem']}**")
                    st.markdown(f"→ *Solution:* {issue['solution']}")
                    st.markdown("")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Link to full help
            if st.button("📖 View Full Documentation", key=f"help_link_{page_name}"):
                st.switch_page("pages/9_help.py")


def render_section_tip(title: str, content: str, icon: str = "💡"):
    """
    Renders an inline help tip for a specific section
    """
    with st.expander(f"{icon} {title}", expanded=False):
        st.markdown(content)