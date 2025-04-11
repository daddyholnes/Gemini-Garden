import streamlit as st
import os
# Import model and theme utilities
from utils.models import generate_chat_response, SUPPORTED_MODELS
from utils.themes import apply_theme
# Import GCS history functions
from utils.gcs_history import load_history, save_history, delete_history 

# --- Page Configuration (First st command) ---
st.set_page_config(
    page_title="Main Chat - Gemini's Garden",
    page_icon="🧠",
    layout="wide"
)

# --- Apply Theme --- 
theme_name = "Dark Purple" # Or dynamically set this
css = apply_theme(theme_name)
st.markdown(css, unsafe_allow_html=True)

# --- Session State Initialization --- 
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_model" not in st.session_state: # Use a different key for the currently active chat model
    st.session_state.current_model = None
if "selected_model_key" not in st.session_state: # Key for the dropdown selection
    st.session_state.selected_model_key = list(SUPPORTED_MODELS.keys())[0] if SUPPORTED_MODELS else None
if "current_temperature" not in st.session_state:
    st.session_state.current_temperature = float(os.environ.get("DEFAULT_TEMPERATURE", 0.7))
if "history_loaded_for_model" not in st.session_state: # Track if history was loaded for the current model
    st.session_state.history_loaded_for_model = None

available_models = list(SUPPORTED_MODELS.keys())

# --- Sidebar --- 
with st.sidebar:
    st.title("⚙️ Configuration")

    # Model Selection
    st.subheader("Select Model")
    if available_models:
        try:
            current_model_index = available_models.index(st.session_state.selected_model_key)
        except (ValueError, TypeError):
            current_model_index = 0

        selected_key_from_dropdown = st.selectbox(
            "AI Model:",
            available_models,
            index=current_model_index,
            key="selected_model_selector"
        )
        
        # *** Check if model selection changed ***
        if selected_key_from_dropdown != st.session_state.selected_model_key:
            st.session_state.selected_model_key = selected_key_from_dropdown
            st.session_state.current_model = selected_key_from_dropdown # Update the active model
            st.session_state.messages = [] # Clear messages when switching models
            st.session_state.history_loaded_for_model = None # Reset history loaded flag
            st.rerun() # Rerun immediately to load new history
        elif st.session_state.current_model is None: # Handle initial load
             st.session_state.current_model = selected_key_from_dropdown

    else:
        st.warning("No models available.")
        st.session_state.selected_model_key = None
        st.session_state.current_model = None

    # Model Settings
    st.subheader("Model Settings")
    st.session_state.current_temperature = st.slider(
        "Temperature", 0.0, 1.0, st.session_state.current_temperature, 0.05, key="temperature_slider"
    )

    # Clear Chat Button
    st.divider()
    if st.button("🗑️ Clear Current Chat History", key="clear_chat_button"):
        if st.session_state.current_model:
            # Delete history from GCS first
            delete_history(st.session_state.current_model)
            # Clear local state
            st.session_state.messages = []
            st.session_state.history_loaded_for_model = None # Ensure it reloads empty next time
            st.rerun()
        else:
            st.warning("No model selected to clear history for.")

# --- Load History Logic --- 
# Load history only once per model selection or if messages are empty
if st.session_state.current_model and st.session_state.history_loaded_for_model != st.session_state.current_model:
    print(f"Loading history for: {st.session_state.current_model}") # Debug print
    st.session_state.messages = load_history(st.session_state.current_model)
    st.session_state.history_loaded_for_model = st.session_state.current_model # Mark history as loaded
    if not st.session_state.messages: 
        print("No history found or loaded, starting fresh.") # Debug print
    # st.rerun() # Rerun after loading history to ensure display


# --- Main Chat Area --- 
st.title("💬 Gemini's Garden - Chat")

# Use columns to create a centered chat area
col1, col2, col3 = st.columns([1, 6, 1]) 

with col2:
    chat_display_container = st.container() # height styling might need CSS adjustments
    with chat_display_container:
        # Display messages currently in session state
        for message in st.session_state.messages:
            avatar = "👤" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

# Chat input
user_input = st.chat_input(f"Chat with {st.session_state.current_model}...")

if user_input and st.session_state.current_model:
    # 1. Append user message to state
    st.session_state.messages.append({"role": "user", "content": user_input})
    # 2. Save updated history immediately after user input
    save_history(st.session_state.current_model, st.session_state.messages)
    # 3. Rerun to display user message and trigger AI response generation below
    st.rerun()

elif user_input and not st.session_state.current_model:
    st.warning("Please select a model from the sidebar first.")

# --- AI Response Generation --- 
# Check if the last message is from the user AND if a model is selected
if st.session_state.current_model and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user_message = st.session_state.messages[-1]["content"]

    with col2:
        with chat_display_container:
             # Find the message placeholder within the container to stream to
             with st.chat_message("assistant", avatar="🤖"):
                try:
                    response_generator = generate_chat_response(
                        selected_model_key=st.session_state.current_model,
                        prompt=last_user_message,
                        message_history=st.session_state.messages[:-1],
                        image_data=None,
                        audio_data=None,
                        temperature=st.session_state.current_temperature,
                        stream=True
                    )
                    full_response = st.write_stream(response_generator)

                    # 4. Append the full AI response to state
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    # 5. Save history again AFTER AI response is complete
                    save_history(st.session_state.current_model, st.session_state.messages)
                    # 6. Rerun *after* saving to finalize the display state (optional, st.write_stream might handle it)
                    st.rerun()

                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"
                    st.error(error_message)
                    # Optionally add error to history and save?
                    # st.session_state.messages.append({"role": "assistant", "content": error_message})
                    # save_history(st.session_state.current_model, st.session_state.messages)
                    # st.rerun()

