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
    return THEMES.get(theme_name, THEMES["Default Blue"])

def apply_theme(theme_name):
    """Generate CSS for the selected theme"""
    theme = get_theme(theme_name)
    st.session_state.theme = theme

    # Generate custom CSS string with updated selectors
    css = f"""
    <style>
        /* Main app background */
        .stApp {{
            background-color: {theme["background"]};
            color: {theme["text"]};
        }}

        /* Sidebar styling */
        section[data-testid="stSidebar"] > div:first-child {{
            background-color: {theme["secondary_bg"]};
        }}

        /* Chat message styling using Streamlit's specific data-testid attributes */
        div[data-testid="stChatMessage"], div[data-testid="stChatMessage"] p {{
             color: {theme["text"]}; /* Ensure text inside message is colored */
        }}

        /* User message bubble styling */
        div[data-testid="stChatMessage"][data-testid*="user"] div[data-testid="stMarkdownContainer"] > div {{
             background-color: {theme["message_user_bg"]};
             border-radius: 18px;
             padding: 10px 15px;
             margin: 2px 5px; /* Adjust margins slightly */
             display: inline-block;
             max-width: 80%;
             float: right; /* Align user messages to the right */
             clear: both; /* Ensure proper clearing */
        }}

        /* AI message bubble styling */
        div[data-testid="stChatMessage"][data-testid*="assistant"] div[data-testid="stMarkdownContainer"] > div {{
             background-color: {theme["message_ai_bg"]};
             border-radius: 18px;
             padding: 10px 15px;
             margin: 2px 5px;
             display: inline-block;
             max-width: 80%;
             float: left; /* Align assistant messages to the left */
             clear: both; /* Ensure proper clearing */
        }}

        /* Clear floats after each message block to prevent overlap */
         div[data-testid="stChatMessage"] {{
             clear: both;
             overflow: auto; /* Contain floats */
             margin-bottom: 10px; /* Add space between messages */
         }}

        /* Input box styling */
        .stChatInputContainer {{
            background-color: {theme["secondary_bg"]};
            border-top: 1px solid #444;
            padding: 15px 20px; /* More padding */
        }}
        textarea[data-testid="stChatInput"] {{
             background-color: {theme["background"]};
             color: {theme["text"]};
             border-radius: 10px;
             border: 1px solid #555; /* Slightly lighter border */
             padding: 10px;
        }}
        textarea[data-testid="stChatInput"]:focus {{
             border-color: {theme["primary"]};
             box-shadow: 0 0 0 1px {theme["primary"]};
        }}

        /* Button styling */
        .stButton > button {{
            background-color: {theme["primary"]};
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 18px; /* Slightly larger padding */
            font-weight: 500;
        }}
        .stButton > button:hover {{
             filter: brightness(1.1); /* Slight brighten on hover */
             box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .stButton > button:active {{
             filter: brightness(0.9); /* Slight darken on click */
        }}

        /* Dropdown styling */
        .stSelectbox > div > div {{
            background-color: {theme["secondary_bg"]};
            color: {theme["text"]};
            border: 1px solid #555;
            border-radius: 8px;
        }}

        /* Header styling */
        h1, h2, h3 {{
            color: {theme["header_color"]};
        }}

        /* General text color */
        body, p, div, span, label {{
            color: {theme["text"]};
        }}

        /* Link color */
        a {{
           color: {theme["accent"]};
        }}

        /* Center chat container - Requires careful structuring in the Python code */
        .centered-chat-container {{
             max-width: 900px; /* Adjust max-width as needed */
             margin: auto; /* Center horizontally */
             /* Add padding or other styles if desired */
        }}

    </style>
    """
    return css
