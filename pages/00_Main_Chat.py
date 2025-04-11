import streamlit as st
from utils.gemini_api import get_model_personality
from utils.themes import apply_theme

# Set page configuration
st.set_page_config(
    page_title="Main Chat - Gemini AI Studio",
    page_icon="🧠",
    layout="wide"
)

# Apply theme
apply_theme("dark-purple")

# Sidebar for personality selection
st.sidebar.title("Personality Selector")
selected_personality = st.sidebar.selectbox(
    "Choose a Personality:",
    ["Default", "Creative & Imaginative", "Analytical & Precise", "Friendly & Supportive", "Custom..."]
)

if selected_personality == "Custom...":
    custom_instructions = st.sidebar.text_area("Custom Personality Instructions:")
    if st.sidebar.button("Save Custom Personality"):
        st.session_state.custom_personality = custom_instructions
        st.sidebar.success("Custom personality saved!")

# Main chat area
st.title("Gemini AI Studio - Main Chat")

# Chat container
chat_container = st.container()
with chat_container:
    st.markdown("### Chat with Gemini AI")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])

    # Input box for user messages
    user_input = st.chat_input("Type your message here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Placeholder for AI response
        ai_response = get_model_personality(
            user_id=1,  # Replace with actual user ID
            model_name="gemini-2.0-pro",
            personality_name=selected_personality.lower()
        )
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.experimental_rerun()