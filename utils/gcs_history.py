"""
Handles saving and loading chat history to/from Google Cloud Storage.
"""
import os
import json
import streamlit as st
from google.cloud import storage
from google.api_core import exceptions
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration --- 
# Get bucket name from environment variable
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")
HISTORY_DIR = "chat_histories/" # Store histories in a subdirectory within the bucket

# --- GCS Client Initialization --- 
_storage_client = None
def get_gcs_client():
    """Initializes and returns a GCS client (singleton pattern)."""
    global _storage_client
    if _storage_client is None:
        try:
            # When running on GCP (Cloud Run, App Engine, GCE), credentials
            # are usually automatically discovered if the service account has permissions.
            # For local development, set GOOGLE_APPLICATION_CREDENTIALS env var.
            _storage_client = storage.Client()
        except Exception as e:
            st.error(f"Failed to initialize Google Cloud Storage client: {e}")
            st.error("Ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly for local dev, or the service account has permissions on GCP.")
            # Set client to an object that indicates failure to prevent repeated errors
            _storage_client = False 
    
    # Return the client if initialization was successful, otherwise None
    return _storage_client if _storage_client else None

# --- History Management Functions --- 
def get_history_blob_name(history_id: str) -> str:
    """Creates the full GCS blob path for a given history ID."""
    # Sanitize history_id slightly - replace spaces, common problematic chars
    safe_id = history_id.replace(" ", "_").replace("/", "-").replace("", "-")
    # Add a .json extension
    return f"{HISTORY_DIR}{safe_id}.json"

def save_history(history_id: str, messages: list):
    """Saves the chat message list to a GCS blob."""
    if not GCS_BUCKET_NAME:
        # Don't show error if bucket isn't configured, just skip saving
        # st.warning("GCS_BUCKET_NAME environment variable not set. Cannot save history.")
        return
    if not messages:
        # Don't save empty history, maybe delete existing?
        # delete_history(history_id) # Decide if empty list should delete file
        return 

    client = get_gcs_client()
    if not client:
        return # Initialization failed earlier

    try:
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob_name = get_history_blob_name(history_id)
        blob = bucket.blob(blob_name)

        # Convert message list to JSON string
        history_json = json.dumps(messages, indent=2)

        # Upload the JSON string
        blob.upload_from_string(history_json, content_type='application/json')
        # st.toast(f"History '{history_id}' saved.", icon="💾") # Optional feedback

    except exceptions.NotFound:
        st.error(f"GCS Bucket '{GCS_BUCKET_NAME}' not found. Please create it and ensure permissions.")
    except Exception as e:
        st.error(f"Failed to save history '{history_id}' to GCS: {e}")

def load_history(history_id: str) -> list:
    """Loads chat message list from a GCS blob. Returns empty list if not found."""
    if not GCS_BUCKET_NAME:
        return [] 

    client = get_gcs_client()
    if not client:
        return [] # Initialization failed earlier

    try:
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob_name = get_history_blob_name(history_id)
        blob = bucket.blob(blob_name)

        # Download JSON string
        history_json = blob.download_as_string()

        # Parse JSON string to list
        messages = json.loads(history_json)
        # st.toast(f"History '{history_id}' loaded.", icon="📂") # Optional feedback
        return messages

    except exceptions.NotFound:
        # If the blob doesn't exist, it's just a new chat, return empty list
        return []
    except Exception as e:
        st.error(f"Failed to load history '{history_id}' from GCS: {e}")
        return [] # Return empty list on other errors

def delete_history(history_id: str):
    """Deletes a chat history file from GCS."""
    if not GCS_BUCKET_NAME:
        return

    client = get_gcs_client()
    if not client:
        return

    try:
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob_name = get_history_blob_name(history_id)
        blob = bucket.blob(blob_name)
        blob.delete()
        # st.toast(f"History '{history_id}' deleted.", icon="🗑️")
    except exceptions.NotFound:
        pass # File already gone
    except Exception as e:
        st.error(f"Failed to delete history '{history_id}' from GCS: {e}")

