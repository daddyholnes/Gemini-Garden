"""
Color themes for AI Chat Studio
"""
import streamlit as st

# Available themes
THEMES = {
    "Default Blue": {
        "primary": "#4285F4",
        "background": "#0E1117",
        "secondary_bg": "#1E1E1E",
        "text": "#FFFFFF",
        "accent": "#4285F4",
        "header_color": "#4285F4",
        "message_user_bg": "#303030",
        "message_ai_bg": "#1e1e1e",
    },
    "Amazon Q Purple": {
        "primary": "#8c52ff",
        "background": "#121212",
        "secondary_bg": "#1A1A1A",
        "text": "#FFFFFF",
        "accent": "#8c52ff",
        "header_color": "#8c52ff",
        "message_user_bg": "#292929",
        "message_ai_bg": "#1d1d1d",
    },
    "Dark Teal": {
        "primary": "#00BFA5",
        "background": "#0F1419",
        "secondary_bg": "#1A1E23",
        "text": "#E0E0E0",
        "accent": "#00BFA5",
        "header_color": "#00BFA5",
        "message_user_bg": "#2A2E33",
        "message_ai_bg": "#1A1E23",
    },
    "Midnight": {
        "primary": "#BB86FC", # A lighter purple for primary actions
        "background": "#121212", # Very dark background
        "secondary_bg": "#1F1F1F", # Slightly lighter dark for secondary elements
        "text": "#E0E0E0", # Light grey text for readability
        "accent": "#BB86FC", # Purple accent
        "header_color": "#BB86FC",
        "message_user_bg": "#2D2D2D", # Darker grey for user messages
        "message_ai_bg": "#1F1F1F", # Even darker for AI messages
    },
    "Ocean": {
        "primary": "#03A9F4",
        "background": "#102A43",
        "secondary_bg": "#1C3A57",
        "text": "#F0F4F8",
        "accent": "#03A9F4",
        "header_color": "#03A9F4",
        "message_user_bg": "#2B4C6F",
        "message_ai_bg": "#1C3A57",
    },
    # Added Dark Purple Theme
    "Dark Purple": {
        "primary": "#9B59B6",  # A distinct purple
        "background": "#1C1C1E",  # Dark background, slightly lighter than pure black
        "secondary_bg": "#2C2C2E",  # Dark grey for sidebar, inputs
        "text": "#E5E5E7",      # Off-white text
        "accent": "#AF7AC5",      # Lighter purple for accents
        "header_color": "#9B59B6",
        "message_user_bg": "#3A3A3C",  # Slightly lighter grey for user bubble
        "message_ai_bg": "#2C2C2E",      # Matching secondary background for AI bubble
    }
}

def get_theme(theme_name):
    """Get a specific theme by name, defaulting to Default Blue if not found"""
    # Corrected default logic to use "Default Blue" if theme_name is not found
    return THEMES.get(theme_name, THEMES["Default Blue"])

def apply_theme(theme_name):
    """Generate CSS for the selected theme"""
    # Use the corrected get_theme function
    theme = get_theme(theme_name)

    # Update the theme in session state for potential JS use or other checks
    st.session_state.theme = theme

    # Generate custom CSS string
    # (CSS rules remain the same as before, just using the selected theme colors)
    css = f"""
    <style>
        /* Main container styling */
        .main {{
            background-color: {theme["background"]};
            color: {theme["text"]};
        }}

        /* Chat container styling */
        .chat-container {{
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
            max-height: 85vh; /* Limit height */
            overflow-y: auto; /* Enable scroll */
        }}

        /* User message styling */
        div[data-testid="chatAvatarIcon-user"] + div div[data-testid="stMarkdownContainer"] > div {{
             background-color: {theme["message_user_bg"]};
             border-radius: 15px;
             padding: 10px 15px;
             margin-right: 5px; /* Add some space from the avatar */
             margin-left: 5px;
             display: inline-block; /* Fit content */
             max-width: 80%; /* Prevent messages from being too wide */
        }}

        /* AI message styling */
         div[data-testid="chatAvatarIcon-assistant"] + div div[data-testid="stMarkdownContainer"] > div {{
             background-color: {theme["message_ai_bg"]};
             border-radius: 15px;
             padding: 10px 15px;
             margin-right: 5px;
             margin-left: 5px;
             display: inline-block; /* Fit content */
             max-width: 80%; /* Prevent messages from being too wide */
        }}

        /* Sidebar styling (using a more stable selector if possible) */
        section[data-testid="stSidebar"] > div:first-child {{
            background-color: {theme["secondary_bg"]};
        }}

        /* Input box styling */
        .stChatInputContainer {{
            background-color: {theme["secondary_bg"]};
            border-top: 1px solid {theme["secondary_bg"]}; /* Match background */
            padding: 10px 15px;
        }}

         /* Input Text Area */
        textarea[data-testid="stChatInput"] {{
             background-color: {theme["background"]};
             color: {theme["text"]};
             border-radius: 10px;
             border: 1px solid #444;
        }}

        /* Button styling */
        .stButton > button {{
            background-color: {theme["primary"]};
            color: white;
            border-radius: 8px;
            border: none;
            padding: 8px 16px;
        }}
        .stButton > button:hover {{
             opacity: 0.8;
        }}

        /* Dropdown styling */
        .stSelectbox > div > div {{
            background-color: {theme["secondary_bg"]};
            color: {theme["text"]};
            border: 1px solid #444;
            border-radius: 8px;
        }}

        /* Header styling */
        h1, h2, h3 {{
            color: {theme["header_color"]}; /* Use specific header color */
        }}

        /* General text color */
        body, p, div, span {{
            color: {theme["text"]};
        }}

        /* Link color */
        a {{
           color: {theme["accent"]};
        }}

    </style>
    """

    # Return the CSS string to be applied using st.markdown
    return css
