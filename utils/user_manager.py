
import streamlit as st
from supabase import create_client, Client
import pandas as pd
import json
from datetime import datetime

class UserManager:
    def __init__(self):
        try:
            self.url = st.secrets["supabase"]["url"]
            self.key = st.secrets["supabase"]["key"]
            self.client: Client = create_client(self.url, self.key)
            self.is_connected = True
        except Exception as e:
            # Silently fail if secrets are missing (app should still work locally without persistence)
            print(f"Supabase connection failed: {e}")
            self.is_connected = False

    def _sanitize_config(self, config):
        """
        Recursively sanitize configuration dictionary to make it JSON-serializable.
        Converts Timestamps, datetime objects, and other non-serializable types.
        """
        if isinstance(config, dict):
            return {key: self._sanitize_config(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._sanitize_config(item) for item in config]
        elif isinstance(config, (pd.Timestamp, datetime)):
            return config.isoformat()
        elif hasattr(config, '__dict__'):
            # Convert objects with __dict__ to dictionaries
            return self._sanitize_config(config.__dict__)
        else:
            # Return as-is for basic types (str, int, float, bool, None)
            return config

    def save_user_profile(self, email, age_group, occupation, config):
        """
        Saves user profile and configuration to Supabase.
        Upserts based on email.
        """
        if not self.is_connected:
            return False

        # Sanitize config to ensure JSON serializability
        sanitized_config = self._sanitize_config(config)

        data = {
            "email": email,
            "age_group": age_group,
            "occupation": occupation,
            "config": sanitized_config,
            "last_updated": datetime.now().isoformat()
        }

        try:
            # Using upsert to handle both new users and updates
            self.client.table("user_configs").upsert(data).execute()
            return True
        except Exception as e:
            st.error(f"Failed to save profile: {e}")
            return False

    def get_user_config(self, email):
        """
        Retrieves the last configuration for a given email.
        """
        if not self.is_connected:
            return None

        try:
            response = self.client.table("user_configs").select("config").eq("email", email).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]['config']
            return None
        except Exception as e:
            print(f"Failed to fetch config: {e}")
            return None
