import streamlit as st
from supabase import create_client, Client

class SupabaseDB:
    def __init__(self):
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            self.client = create_client(url, key)
        except Exception as e:
            print(f"Failed to initialize Supabase client: {e}")

    def get_client(self) -> Client:
        if not self.client:
            self._init_client()
        return self.client

db = SupabaseDB()
