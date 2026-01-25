import streamlit as st
from supabase import create_client, Client

class SupabaseDB:
    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        import os
        try:
            # Try Streamlit secrets first
            if "supabase" in st.secrets:
                url = st.secrets["supabase"]["url"]
                key = st.secrets["supabase"]["key"]
            else:
                # Fallback to Environment Variables (common in Render/Docker)
                url = os.environ.get("SUPABASE_URL")
                key = os.environ.get("SUPABASE_KEY")
            
            if url and key:
                self.client = create_client(url, key)
            else:
                print("Supabase credentials not found in secrets or environment variables.")
        except Exception as e:
            print(f"Failed to initialize Supabase client: {e}")

    def get_client(self) -> Client:
        if not self.client:
            self._init_client()
        return self.client

db = SupabaseDB()
