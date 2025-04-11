import streamlit as st
# Import from the refactored models utility
from utils.models import generate_chat_response, SUPPORTED_MODELS
from utils.themes import apply_theme # Import the function that *generates* CSS
import os # Import os to potentially get temperature from environment or default

# Set page configuration (should be the first st command)
st.set_page_config(
    page_title="Main Chat - Gemini's Garden",
    page_icon="🧠",
    layout="wide" # Use wide layout
)

# --- Apply Theme --- 
# Get the CSS string for the desired theme
theme_name = "Dark Purple" # Or dynamically set this, e.g., from session state or a selector
css = apply_theme(theme_name)
# Apply the CSS using st.markdown
st.markdown(css, unsafe_allow_html=True)

# --- Session State Initialization --- 
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize selected model if it doesn't exist
available_models = list(SUPPORTED_MODELS.keys())
if "selected_model" not in st.session_state:
    # Ensure available_models is not empty before accessing index 0
    if available_models:
        st.session_state.selected_model = available_models[0]
    else:
        st.session_state.selected_model = None # Handle case with no models

# --- Sidebar --- 
st.sidebar.title("Chat Configuration")

# Model Selection
st.sidebar.subheader("Select Model")
if available_models:
    # Use index parameter to set default based on session state
    try:
        current_model_index = available_models.index(st.session_state.selected_model)
    except ValueError:
        current_model_index = 0 # Default to first if state model isn't in list

    selected_model_key = st.sidebar.selectbox(
        "Choose the AI model:",
        available_models,
        index=current_model_index,
        key="selected_model_selector" # Use a distinct key for the widget itself
    )
    # Update session state if selection changes
    st.session_state.selected_model = selected_model_key
else:
    st.sidebar.warning("No models available. Check configuration.")
    st.session_state.selected_model = None

# Placeholder for Temperature/Personality settings
st.sidebar.subheader("Model Settings")
current_temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.05, key="temperature_slider")
st.session_state.current_temperature = current_temperature
# Add Personality selector later if needed

# Clear Chat Button
if st.sidebar.button("Clear Chat History", key="clear_chat_button"):
    st.session_state.messages = []
    st.rerun() # Rerun to reflect the cleared history immediately

# --- Main Chat Area --- 
st.title("💬 Gemini's Garden - Chat")

# Define chat container with explicit height and scroll
# Note: Direct height styling via st.container() isn't standard.
# CSS applied earlier should handle the scroll and appearance.
chat_display_container = st.container()

with chat_display_container:
    # Display chat messages from history
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Use st.chat_input outside the display container for fixed position
user_input = st.chat_input(f"Chat with {st.session_state.selected_model}...")

if user_input and st.session_state.selected_model:
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message immediately in the container
    with chat_display_container:
         with st.chat_message("user", avatar="👤"):
             st.markdown(user_input)

    # --- Generate AI response --- 
    # Display thinking indicator in the chat display container
    with chat_display_container:
        with st.chat_message("assistant", avatar="🤖"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("🧠 Thinking...")

            try:
                # Call the central function with the selected model key and temperature
                ai_response = generate_chat_response(
                    selected_model_key=st.session_state.selected_model,
                    prompt=user_input,
                    message_history=st.session_state.messages, # Pass history up to the user's latest message
                    image_data=None, # Placeholder for future multimodal input
                    audio_data=None, # Placeholder
                    temperature=st.session_state.current_temperature
                )
            except Exception as e:
                ai_response = f"An error occurred: {str(e)}"
                st.error(ai_response) # Display error in the app

            # Replace thinking indicator with actual response
            thinking_placeholder.markdown(ai_response)

    # Add AI response to state AFTER displaying
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # Trigger a rerun to ensure the message list updates correctly at the end
    st.rerun()

elif user_input and not st.session_state.selected_model:
    # Handle case where user types but no model is selected/available
     with chat_display_container:
         st.warning("Please select a model from the sidebar first.")

