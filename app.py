from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

import streamlit as st
import os

# --- Function to load CSS ---
def load_css(file_path):
    try:
        with open(file_path, "r") as f:
            css = f.read()
        return f"<style>{css}</style>"
    except FileNotFoundError:
        st.error(f"CSS file not found at {file_path}")
        return ""

# --- Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(
    page_title="Gemini's Garden", # Updated title
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Apply Custom CSS ---
# Load the CSS from the specified path
custom_css = load_css("docs/UI/css/main.css")
if custom_css:
    st.markdown(custom_css, unsafe_allow_html=True)

# --- Minimalist App Entry Point ---
# This file now primarily serves to set the page config.
# Streamlit automatically discovers and lists files in the 'pages/' directory
# in the sidebar for navigation.

# You could add a simple landing page message here if desired,
# but it's often cleaner to let the first page in the 'pages/'
# directory (sorted alphabetically, e.g., 00_Main_Chat.py) be the default view.

st.title("Welcome to Gemini's Garden")
st.write("Please select a page from the sidebar to begin.")

# --- Authentication Check (Optional - Keeping it simple for now) ---
# We are bypassing authentication for now to use the multipage structure directly.
# To re-enable authentication later (e.g., Google OAuth), you would:
# 1. Uncomment the import: from utils.google_auth import check_login, logout_user
# 2. Uncomment the call: check_login()
# 3. Add a logout button to the sidebar (conditionally if logged in)

# --- Database Initialization (Optional - can be done per-page if needed) ---
# from utils.database import init_db
# init_db() # Initialize DB tables if needed globally

# The rest of the UI and application logic is now handled by the files
# in the 'pages/' directory (e.g., pages/00_Main_Chat.py).
