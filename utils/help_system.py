"""
SIMPLEST Help System - Just Big "?" Text
No complex CSS fighting, just big text in button
"""

import streamlit as st

def render_help_button(page_name: str):
    """
    Simplest help button - just big "?" text
    """
    
    # Import help content
    try:
        from .help_content import HELP_CONTENT
    except:
        from help_content import HELP_CONTENT
    
    # Get help content
    help_data = HELP_CONTENT.get(page_name)
    if not help_data:
        return
    
    # Minimal CSS - just for help content, no button styling
    st.markdown("""
    <style>
        /* Help content styling only */
        .help-content-box {
            background: linear-gradient(180deg, #1a1f3a 0%, #0f1419 100%);
            border: 2px solid rgba(139, 92, 246, 0.5);
            border-radius: 16px;
            padding: 26px;
            margin: 25px 0;
            max-height: 650px;
            overflow-y: auto;
            color: #e2e8f0;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        }
        
        .help-content-box h2 {
            color: #ffffff;
            margin-top: 0;
            font-size: 2em;
            background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .help-content-box h3 {
            color: #c4b5fd;
            margin-top: 24px;
            margin-bottom: 14px;
            font-size: 1.4em;
            border-bottom: 3px solid rgba(139, 92, 246, 0.4);
            padding-bottom: 10px;
        }
        
        .help-tip-box {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(236, 72, 153, 0.2) 100%);
            border-left: 6px solid #8b5cf6;
            padding: 18px;
            border-radius: 10px;
            margin: 18px 0;
            color: #e2e8f0;
        }
        
        .help-feature-item {
            margin-bottom: 16px;
            padding: 16px;
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(236, 72, 153, 0.12) 100%);
            border-radius: 12px;
            border-left: 5px solid #8b5cf6;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Session state
    if f'show_help_{page_name}' not in st.session_state:
        st.session_state[f'show_help_{page_name}'] = False
    
    # Simple layout - button in rightmost column
    col1, col2 = st.columns([0.92, 0.08])
    
    with col2:
        # Use larger emoji or text - simple solution!
        # Option 1: Use emoji (automatically bigger)
        if st.button("❓", key=f"help_btn_{page_name}", help="Click for help"):
            st.session_state[f'show_help_{page_name}'] = not st.session_state[f'show_help_{page_name}']
    
    # Show help content
    if st.session_state[f'show_help_{page_name}']:
        st.markdown("---")
        
        with st.container():
            st.markdown(f"""
            <div class='help-content-box'>
                <h2>{help_data['title']}</h2>
                <p style='color: #cbd5e1; font-size: 1.15em;'>{help_data['overview']}</p>
            """, unsafe_allow_html=True)
            
            if help_data.get('features'):
                st.markdown("### Key Features")
                for feature in help_data['features']:
                    st.markdown(f"""
                    <div class='help-feature-item'>
                        <strong>{feature['name']}</strong><br>
                        {feature['description']}
                    </div>
                    """, unsafe_allow_html=True)
            
            if help_data.get('how_to_use'):
                st.markdown("### How to Use")
                for i, step in enumerate(help_data['how_to_use'], 1):
                    st.markdown(f"{i}. {step}")
            
            if help_data.get('tips'):
                st.markdown('<div class="help-tip-box"><strong>💡 Pro Tips</strong></div>', unsafe_allow_html=True)
                for tip in help_data['tips']:
                    st.markdown(f"- {tip}")
            
            if help_data.get('common_issues'):
                st.markdown("### Common Issues")
                for issue in help_data['common_issues']:
                    st.markdown(f"**❓ {issue['problem']}**")
                    st.markdown(f"✓ Solution: {issue['solution']}")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("📖 Full Documentation", key=f"help_link_{page_name}", type="primary"):
                    st.switch_page("pages/9_Help.py")
            with col_b:
                if st.button("✖ Close", key=f"close_help_{page_name}"):
                    st.session_state[f'show_help_{page_name}'] = False
                    st.rerun()
        
        st.markdown("---")


def render_section_tip(title: str, content: str, icon: str = "💡 Tip"):
    """Inline help tip for specific sections"""
    with st.expander(f"{icon} {title}", expanded=False):
        st.markdown(content)