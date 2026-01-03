import streamlit as st
import pandas as pd
import io
import json

def get_table_download_link(df, filename, format):
    """Generates a link to download the dataframe in the specified format"""
    output = io.BytesIO()
    
    if format == 'CSV':
        df.to_csv(output, index=False)
        mime = "text/csv"
        ext = "csv"
    elif format == 'Excel':
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"
    elif format == 'JSON':
        df_json = df.to_json(orient="records", indent=4)
        output.write(df_json.encode())
        mime = "application/json"
        ext = "json"
    
    return output.getvalue(), mime, f"{filename}.{ext}"

@st.cache_data(show_spinner="Generating image...")
def get_plot_download_link(fig_json, filename, format):
    """Generates bytes for downloading the plotly figure in the specified format"""
    import plotly.io as pio
    import json
    
    # Load figure from JSON string (easier to hash)
    fig = pio.from_json(fig_json)
    
    try:
        # Plotly's to_image requires kaleido
        img_bytes = fig.to_image(format=format.lower(), scale=2)
        
        if format == 'PNG':
            mime = "image/png"
        elif format == 'JPG':
            mime = "image/jpeg"
        elif format == 'SVG':
            mime = "image/svg+xml"
        elif format == 'PDF':
            mime = "application/pdf"
        
        return img_bytes, mime, f"{filename}.{format.lower()}"
    except Exception as e:
        return None, None, str(e)

def export_data_menu(df, filename="data_export", key=None):
    """Renders a download menu for dataframes"""
    with st.popover("📥 Export Data", use_container_width=True):
        st.write("Choose format:")
        col1, col2, col3 = st.columns(3)
        
        # CSV
        data, mime, fname = get_table_download_link(df, filename, 'CSV')
        col1.download_button("CSV", data, fname, mime, key=f"{key}_csv" if key else None, use_container_width=True)
        
        # Excel
        data, mime, fname = get_table_download_link(df, filename, 'Excel')
        col2.download_button("Excel", data, fname, mime, key=f"{key}_xlsx" if key else None, use_container_width=True)
        
        # JSON
        data, mime, fname = get_table_download_link(df, filename, 'JSON')
        col3.download_button("JSON", data, fname, mime, key=f"{key}_json" if key else None, use_container_width=True)

def export_plot_menu(fig, filename="plot_export", key=None):
    """Renders a download menu for Plotly figures with a downarrow icon"""
    with st.popover("🔽 Download Plot", use_container_width=True):
        st.write("Choose image format:")
        
        # Convert to JSON for caching
        try:
            fig_json = fig.to_json()
        except:
            st.error("Could not process plot for download.")
            return
            
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
        # Common formats supported by Kaleido
        formats = ['PNG', 'JPG', 'SVG', 'PDF']
        
        for i, fmt in enumerate(formats):
            target_col = [col1, col2, col3, col4][i]
            data, mime, fname = get_plot_download_link(fig_json, filename, fmt)
            
            if data:
                target_col.download_button(
                    label=f"📥 {fmt}",
                    data=data,
                    file_name=fname,
                    mime=mime,
                    key=f"{key}_{fmt.lower()}" if key else None,
                    use_container_width=True
                )
            else:
                target_col.error(f"Failed {fmt}")
