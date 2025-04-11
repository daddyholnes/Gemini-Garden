import streamlit as st
# Import from the refactored models utility
from utils.models import generate_chat_response, SUPPORTED_MODELS
from utils.themes import apply_theme # Import the function that *generates* CSS
import os

# --- Page Configuration (First st command) ---
st.set_page_config(
    page_title="Main Chat - Gemini's Garden",
    page_icon="🧠",
    layout="wide"
)

# --- Apply Theme --- 
theme_name = "Dark Purple"
css = apply_theme(theme_name)
st.markdown(css, unsafe_allow_html=True)

# --- Session State Initialization --- 
if "messages" not in st.session_state:
    st.session_state.messages = []

available_models = list(SUPPORTED_MODELS.keys())
if "selected_model" not in st.session_state:
    st.session_state.selected_model = available_models[0] if available_models else None
if "current_temperature" not in st.session_state:
    st.session_state.current_temperature = float(os.environ.get("DEFAULT_TEMPERATURE", 0.7))

# --- Sidebar --- 
with st.sidebar:
    st.title("⚙️ Configuration")

    # Model Selection
    st.subheader("Select Model")
    if available_models:
        try:
            current_model_index = available_models.index(st.session_state.selected_model)
        except (ValueError, TypeError): # Handle None or missing model
            current_model_index = 0

        selected_model_key = st.selectbox(
            "AI Model:",
            available_models,
            index=current_model_index,
            key="selected_model_selector"
        )
        st.session_state.selected_model = selected_model_key
    else:
        st.warning("No models available.")
        st.session_state.selected_model = None

    # Model Settings
    st.subheader("Model Settings")
    st.session_state.current_temperature = st.slider(
        "Temperature", 0.0, 1.0, st.session_state.current_temperature, 0.05, key="temperature_slider"
    )

    # Clear Chat Button
    st.divider()
    if st.button("🗑️ Clear Chat History", key="clear_chat_button"):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Area --- 
st.title("💬 Gemini's Garden - Chat")

# Use columns to create a centered chat area
col1, col2, col3 = st.columns([1, 6, 1]) # Adjust ratios as needed

with col2:
    # Container for the chat messages
    chat_display_container = st.container()
    with chat_display_container:
        for message in st.session_state.messages:
            avatar = "👤" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

# Chat input - Placed outside the columns
user_input = st.chat_input(f"Chat with {st.session_state.selected_model}...")

if user_input and st.session_state.selected_model:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun() # Rerun immediately to display user message

elif user_input and not st.session_state.selected_model:
    st.warning("Please select a model from the sidebar first.")

# Handle AI response generation if the last message is from the user
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user_message = st.session_state.messages[-1]["content"]

    # Display AI response within the centered column's chat container
    with col2:
         with chat_display_container:
            with st.chat_message("assistant", avatar="🤖"):
                try:
                    # Call generate_chat_response with stream=True
                    response_generator = generate_chat_response(
                        selected_model_key=st.session_state.selected_model,
                        prompt=last_user_message,
                        message_history=st.session_state.messages[:-1],
                        image_data=None,
                        audio_data=None,
                        temperature=st.session_state.current_temperature,
                        stream=True # Request streaming output
                    )
                    
                    # Use st.write_stream to display the generated chunks
                    # It automatically handles accumulating the response
                    full_response = st.write_stream(response_generator)
                    
                    # Add the *complete* AI response to state AFTER streaming is finished
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    st.rerun() # Rerun to ensure state consistency after adding AI message

                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"
                    st.error(error_message)
                    # Add error message to chat history as well
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
                    st.rerun()

