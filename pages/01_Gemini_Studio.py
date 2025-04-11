"""
Gemini Studio - Advanced multimodal interactions with Gemini models

This page provides an enhanced interface for interacting with the latest Gemini models,
including Gemini 2.0 Pro. It supports:
- Real-time streaming responses
- Multimodal inputs (text, images, audio)
- Webcam integration
- Screen sharing
- Two-way conversation
"""

import streamlit as st
import os
import base64
import json
import time
import datetime
from io import BytesIO
from PIL import Image
import tempfile

# Import Gemini-specific utilities
from utils.gemini_api import (
    initialize_gemini,
    get_gemini_models,
    get_gemini_response,
    get_gemini_streaming_response
)

# Import database utilities for conversation storage
from utils.database import (
    init_db, 
    save_conversation, 
    load_conversations, 
    get_most_recent_chat
)

# Auth utilities
from utils.auth import check_login, get_current_user

# Audio utilities 
from utils.webrtc_audio import audio_recorder_ui

# --- Function to load CSS ---
def load_css(file_path):
    try:
        with open(file_path, "r") as f:
            css = f.read()
        return f"<style>{css}</style>"
    except FileNotFoundError:
        st.error(f"CSS file not found at {file_path}")
        return ""

# Set page title and icon
st.set_page_config(
    page_title="Gemini Studio - AI Chat Studio",
    page_icon="🧠",
    layout="wide"
)

# --- Apply Custom CSS ---
# Load the CSS from the specified path
custom_css = load_css("docs/UI/css/main.css")
if custom_css:
    st.markdown(custom_css, unsafe_allow_html=True)

# Check user login
check_login()

# Initialize session state for this page
if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = []
if "current_model" not in st.session_state:
    st.session_state.current_model = "gemini-1.5-pro"
if "gemini_current_model" not in st.session_state:
    st.session_state.gemini_current_model = "gemini-1.5-pro"
if "gemini_temperature" not in st.session_state:
    st.session_state.gemini_temperature = 0.7
if "gemini_streaming" not in st.session_state:
    st.session_state.gemini_streaming = True
if "gemini_chat_id" not in st.session_state:
    st.session_state.gemini_chat_id = None
if "gemini_uploaded_image" not in st.session_state:
    st.session_state.gemini_uploaded_image = None
if "gemini_webcam_image" not in st.session_state:
    st.session_state.gemini_webcam_image = None
if "gemini_audio_data" not in st.session_state:
    st.session_state.gemini_audio_data = None
if "gemini_screen_share" not in st.session_state:
    st.session_state.gemini_screen_share = None
if "gemini_message_cooldown" not in st.session_state:
    st.session_state.gemini_message_cooldown = False

# Initialize the database
init_db()

# Initialize Gemini API
ai_initialized = initialize_gemini()

def encode_image(uploaded_file):
    """Encode an uploaded file to base64 string"""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        encoded = base64.b64encode(bytes_data).decode('utf-8')
        return encoded
    return None

def clear_multimodal_inputs():
    """Clear all multimodal inputs"""
    st.session_state.gemini_uploaded_image = None
    st.session_state.gemini_webcam_image = None
    st.session_state.gemini_audio_data = None
    st.session_state.gemini_screen_share = None

def load_or_initialize_conversation():
    """Load recent conversation or initialize a new one"""
    username = get_current_user()
    if not username:
        return

    # Load most recent conversation for this model
    chat_id, messages = get_most_recent_chat(
        username=username,
        model=st.session_state.gemini_current_model
    )

    if chat_id and messages:
        st.session_state.gemini_messages = messages
        st.session_state.gemini_chat_id = chat_id
    else:
        # Initialize new conversation
        st.session_state.gemini_messages = []
        st.session_state.gemini_chat_id = None

def save_current_conversation():
    """Save the current conversation to the database"""
    username = get_current_user()
    if not username:
        return

    # Save conversation with the current model
    save_conversation(
        username=username,
        model=st.session_state.gemini_current_model,
        messages=st.session_state.gemini_messages
    )

def main():
    """Main function for the Gemini Studio page"""

    # Display header
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 2.2rem; margin-bottom: 5px;">AI Studio</h1>
        <p style="color: #888; font-size: 1.1rem;">Advanced multimodal interactions with local AI models</p>
        <div style="max-width: 600px; margin: 10px auto; padding: 8px; background-color: #0f0f0f; border-radius: 8px; border: 1px solid #333;">
            <p style="margin: 0; color: #4285f4;">
                <strong>Model:</strong> <span id="current-model">Local-AI-Model</span>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Check if Gemini API is initialized
    if not ai_initialized:
        st.error("AI model not initialized. Please check your configuration.")
        return

    # Create a two-column layout: Chat area and sidebar
    col1, col2 = st.columns([4, 1])

    # Sidebar (col2) - Configuration options
    with col2:
        st.sidebar.title("Gemini Settings")

        # Model selection
        st.sidebar.subheader("Model")
        model_options = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-2.0-pro",
            "gemini-2.0-pro-vision",
            "gemini-2.0-flash"
        ]

        selected_model = st.sidebar.selectbox(
            "Select Gemini Model",
            options=model_options,
            index=model_options.index(st.session_state.gemini_current_model)
            if st.session_state.gemini_current_model in model_options else 0
        )

        # Update the model in session state if changed
        if selected_model != st.session_state.gemini_current_model:
            st.session_state.gemini_current_model = selected_model
            # Load conversation for the new model
            load_or_initialize_conversation()
            st.sidebar.success(f"Loaded conversations for {selected_model}")

        # Temperature slider
        st.sidebar.subheader("Generation Settings")
        temperature = st.sidebar.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.gemini_temperature,
            step=0.1,
            help="Higher values make output more random, lower values more focused"
        )

        # Update temperature if changed
        if temperature != st.session_state.gemini_temperature:
            st.session_state.gemini_temperature = temperature

        # Streaming toggle
        streaming = st.sidebar.checkbox(
            "Enable streaming responses",
            value=st.session_state.gemini_streaming,
            help="Show AI responses as they are generated"
        )

        # Update streaming setting if changed
        if streaming != st.session_state.gemini_streaming:
            st.session_state.gemini_streaming = streaming

        # Conversation management section
        st.sidebar.subheader("Conversation")

        # New conversation button
        if st.sidebar.button("Start New Conversation", use_container_width=True):
            st.session_state.gemini_messages = []
            st.session_state.gemini_chat_id = None
            clear_multimodal_inputs()
            st.sidebar.success("Started new conversation")
            st.rerun()

        # Sidebar for personality selection
        st.sidebar.title("Personality Selector")
        st.sidebar.markdown("Select a personality for the AI model:")
        selected_personality = st.sidebar.selectbox(
            "Choose a Personality:",
            ["Default", "Creative & Imaginative", "Analytical & Precise", "Friendly & Supportive", "Custom..."]
        )

        if selected_personality == "Custom...":
            custom_instructions = st.sidebar.text_area("Custom Personality Instructions:")
            if st.sidebar.button("Save Custom Personality"):
                st.session_state.custom_personality = custom_instructions
                st.sidebar.success("Custom personality saved!")

    # Main chat area (col1)
    with col1:
        # Display chat messages
        messages_container = st.container()
        with messages_container:
            for message in st.session_state.gemini_messages:
                is_user = message["role"] == "user"

                # Create message bubbles
                if is_user:
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"])

                # Handle multimodal content if present
                if isinstance(message.get("content"), list):
                    for part in message["content"]:
                        if isinstance(part, dict):
                            if part.get("type") == "image" and part.get("data"):
                                try:
                                    image_data = base64.b64decode(part["data"])
                                    image = Image.open(BytesIO(image_data))
                                    st.image(image, caption="Shared Image", use_column_width=True)
                                except Exception as e:
                                    st.error(f"Could not display image: {str(e)}")
                            elif part.get("type") == "audio" and part.get("data"):
                                try:
                                    audio_data = base64.b64decode(part["data"])
                                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                                        tmp.write(audio_data)
                                        st.audio(tmp.name)
                                except Exception as e:
                                    st.error(f"Could not play audio: {str(e)}")

        # Multimodal input options
        input_tabs = st.tabs(["Image Upload", "Webcam", "Audio Recording", "Screen Share"])

        # Image upload tab
        with input_tabs[0]:
            uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                # Save the uploaded image to session state
                st.session_state.gemini_uploaded_image = encode_image(uploaded_file)

                # Preview the image
                st.image(uploaded_file, caption="Image ready for analysis", width=300)

                # Show removal button
                if st.button("Remove uploaded image"):
                    st.session_state.gemini_uploaded_image = None
                    st.rerun()

        # Webcam tab
        with input_tabs[1]:
            st.markdown("### Webcam Capture")
            st.markdown("Take a photo with your webcam to include in the conversation")

            webcam_image = st.camera_input("Take a photo")
            if webcam_image:
                # Save webcam image to session state
                st.session_state.gemini_webcam_image = encode_image(webcam_image)

                # Show removal button
                if st.button("Remove webcam image"):
                    st.session_state.gemini_webcam_image = None
                    st.rerun()

        # Audio recording tab
        with input_tabs[2]:
            st.markdown("### Audio Recording")
            st.markdown("Record audio to include in the conversation")

            # Use WebRTC audio recorder
            base64_audio = audio_recorder_ui(
                key="gemini_webrtc_recorder",
                title="Record Audio",
                description="Click start to begin recording. Click stop when done.",
                durations=[15, 30, 60, 120],
                show_description=True,
                show_playback=True
            )

            if base64_audio:
                st.session_state.gemini_audio_data = base64_audio
                st.session_state.gemini_audio_path = st.session_state.get("gemini_webrtc_recorder_file_path")

                st.success("Audio recorded successfully!")
                st.info("You can now send a message to analyze this audio.")

                # Show removal button
                if st.button("Remove recorded audio"):
                    st.session_state.gemini_audio_data = None
                    st.session_state.gemini_audio_path = None
                    st.rerun()

        # Screen share tab
        with input_tabs[3]:
            st.markdown("### Screen Share")
            st.markdown("Currently, screen sharing requires manual screenshot uploads")

            screen_file = st.file_uploader("Upload a screenshot", type=["jpg", "jpeg", "png"], key="screen_upload")
            if screen_file:
                # Save screenshot to session state
                st.session_state.gemini_screen_share = encode_image(screen_file)

                # Preview the screenshot
                st.image(screen_file, caption="Screenshot ready for analysis", width=300)

                # Show removal button
                if st.button("Remove screenshot"):
                    st.session_state.gemini_screen_share = None
                    st.rerun()

            # Note about screen sharing
            st.info("Note: Native screen sharing capabilities will be added in a future update")

        # Text input area
        st.markdown("### Message Input")

        # Get multimodal status
        has_image = st.session_state.gemini_uploaded_image is not None or st.session_state.gemini_webcam_image is not None
        has_audio = st.session_state.gemini_audio_data is not None
        has_screen = st.session_state.gemini_screen_share is not None

        # Show active multimodal inputs
        if has_image or has_audio or has_screen:
            status_items = []
            if has_image:
                status_items.append("📷 Image")
            if has_audio:
                status_items.append("🎤 Audio")
            if has_screen:
                status_items.append("🖥️ Screen")

            status_text = ", ".join(status_items)
            st.info(f"Active inputs: {status_text}")

            # Add a button to clear all multimodal inputs
            if st.button("Clear all inputs"):
                clear_multimodal_inputs()
                st.rerun()

        # Message input area
        chat_container = st.container()
        with chat_container:
            if user_input := st.chat_input("Message the AI...", key="chat_input_main"):
                # Prevent double submissions
                if "processing_message" in st.session_state:
                    st.info("Message already being processed...")
                    return

                st.session_state.processing_message = True

                try:
                    with st.spinner("Processing message..."):
                        # Add user message to chat
                        st.session_state.gemini_messages.append({
                            "role": "user",
                            "content": user_input
                        })

                        # Get AI response based on selected model
                        with st.spinner(f"Thinking... using {st.session_state.gemini_current_model}"):
                            try:
                                # Get any multimodal content
                                multimodal_content = []

                                # Add image if present
                                if st.session_state.gemini_uploaded_image:
                                    multimodal_content.append({
                                        "type": "image",
                                        "data": st.session_state.gemini_uploaded_image
                                    })
                                elif st.session_state.gemini_webcam_image:
                                    multimodal_content.append({
                                        "type": "image",
                                        "data": st.session_state.gemini_webcam_image
                                    })
                                elif st.session_state.gemini_screen_share:
                                    multimodal_content.append({
                                        "type": "image",
                                        "data": st.session_state.gemini_screen_share
                                    })

                                # Add audio if present
                                if st.session_state.gemini_audio_data:
                                    multimodal_content.append({
                                        "type": "audio",
                                        "data": st.session_state.gemini_audio_data
                                    })

                                # Prepare the message content
                                message_content = [user_input]
                                message_content.extend(multimodal_content)

                                # Get AI response
                                if st.session_state.gemini_streaming:
                                    # For streaming responses
                                    response_placeholder = st.empty()
                                    full_response = ""

                                    for response_chunk in get_gemini_streaming_response(
                                        prompt=user_input,
                                        conversation_history=st.session_state.gemini_messages,
                                        image_data=st.session_state.gemini_uploaded_image or st.session_state.gemini_webcam_image or st.session_state.gemini_screen_share,
                                        audio_data=st.session_state.gemini_audio_data,
                                        temperature=st.session_state.gemini_temperature,
                                        model_name=st.session_state.gemini_current_model
                                    ):
                                        full_response += response_chunk
                                        response_placeholder.markdown(full_response)

                                    response = full_response
                                else:
                                    # For non-streaming responses
                                    response = get_gemini_response(
                                        prompt=user_input,
                                        conversation_history=st.session_state.gemini_messages,
                                        image_data=st.session_state.gemini_uploaded_image or st.session_state.gemini_webcam_image or st.session_state.gemini_screen_share,
                                        audio_data=st.session_state.gemini_audio_data,
                                        temperature=st.session_state.gemini_temperature,
                                        model_name=st.session_state.gemini_current_model
                                    )

                                # Add AI response to chat
                                st.session_state.gemini_messages.append({
                                    "role": "assistant",
                                    "content": response
                                })

                                # Clear multimodal inputs after successful processing
                                clear_multimodal_inputs()

                            except Exception as e:
                                st.error(f"Error generating response: {str(e)}")
                            finally:
                                # Clear processing flag
                                if "processing_message" in st.session_state:
                                    del st.session_state.processing_message

                        # Save conversation after adding message
                        save_current_conversation()

                        # Rerun to update UI
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    # Ensure processing flag is cleared even if an error occurs
                    if "processing_message" in st.session_state:
                        del st.session_state.processing_message


# Call main function
if __name__ == "__main__":
    main()
