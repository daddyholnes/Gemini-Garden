"""
WebRTC-based audio recording for Streamlit applications

This module provides enhanced audio recording capabilities using WebRTC,
which offers better quality and real-time processing compared to basic
audio recording.
"""

import base64
import numpy as np
import streamlit as st
import av
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode,
    RTCConfiguration,
    VideoProcessorBase,
    AudioProcessorBase,
    # ClientSettings # Removed this import as it caused an ImportError
)
import tempfile
import os
import time
import uuid

# Configure RTC for STUN servers
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]} # Using Google's public STUN server
)

# Define WebRTC client settings - Removed as ClientSettings import failed
# WEBRTC_CLIENT_SETTINGS = ClientSettings(
#     rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
#     media_stream_constraints={"video": True, "audio": True},
# )

def video_frame_callback(frame):
    """Process video frames for webcam streaming."""
    img = frame.to_ndarray(format="bgr24")
    # Apply any image processing here (e.g., filters, overlays)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

def audio_frame_callback(frame):
    """Process audio frames for TTS or analysis."""
    # Note: This callback might not be directly used by the audio_recorder_ui
    audio = np.frombuffer(frame.to_ndarray(), dtype=np.int16)
    # Apply any audio processing here (e.g., noise reduction)
    return av.AudioFrame.from_ndarray(audio, layout="mono")

def webcam_stream():
    """Start webcam streaming using WebRTC."""
    # Note: Requires ClientSettings or similar configuration to be passed if needed.
    # Currently relies on default settings or RTC_CONFIGURATION only.
    webrtc_streamer(
        key="webcam-stream",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION, # Pass the RTC config
        # client_settings=WEBRTC_CLIENT_SETTINGS, # Removed due to import error
        video_frame_callback=video_frame_callback,
        # audio_frame_callback=audio_frame_callback, # Not typically used for basic streaming
    )

def tts_playback(text):
    """Convert text to speech and play it back."""
    try:
        from gtts import gTTS
        from playsound import playsound

        # Generate TTS audio
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            playsound(tmp.name)
            os.unlink(tmp.name)
    except ImportError:
        st.error("gTTS or playsound not installed. Cannot play TTS.")
    except Exception as e:
        st.error(f"Error playing TTS: {e}")

def screen_share():
    """Enable screen sharing by uploading screenshots."""
    st.markdown("### Screen Sharing")
    screen_file = st.file_uploader("Upload a screenshot", type=["jpg", "jpeg", "png"], key="screen_upload")
    if screen_file:
        st.image(screen_file, caption="Shared Screen", use_column_width=True)

class AudioProcessor(AudioProcessorBase):
    """Audio processor for WebRTC streaming that saves audio frames to a buffer"""

    def __init__(self, max_duration: int = 60):
        """
        Initialize the audio processor with the specified maximum duration

        Args:
            max_duration: Maximum recording duration in seconds
        """
        self.audio_buffer = []
        self.sample_rate = 48000  # WebRTC typically uses 48kHz
        self.channels = 1  # Mono audio
        self.max_frames = max_duration * self.sample_rate
        self.start_time = None
        self.recording_complete = False
        self.stopped = False
        self.output_file = None

        # Create a temporary file to store the audio
        fd, self.output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        """
        Process each incoming audio frame

        Args:
            frame: Audio frame from WebRTC

        Returns:
            The unmodified audio frame
        """
        if self.stopped or self.recording_complete:
            return frame

        if self.start_time is None:
            self.start_time = time.time()

        # Convert frame to numpy array
        sound_array = frame.to_ndarray()

        # Append to buffer
        self.audio_buffer.append(sound_array)

        # Check if we've reached the maximum duration
        total_samples = sum(len(chunk) for chunk in self.audio_buffer)
        if total_samples >= self.max_frames:
            self.recording_complete = True
            self._save_audio()

        return frame

    def stop(self):
        """Stop recording and save the audio file"""
        if not self.stopped:
            self.stopped = True
            self._save_audio()

    def _save_audio(self):
        """Save the recorded audio to a WAV file"""
        if not self.audio_buffer or self.output_file:
             # Don't save if buffer is empty or already saved
            return

        try:
            import soundfile as sf

            # Concatenate all audio chunks
            audio_data = np.concatenate(self.audio_buffer, axis=0)

            # Save as WAV file
            sf.write(
                self.output_path,
                audio_data,
                self.sample_rate,
                format='WAV'
            )

            # Set the output file flag
            self.output_file = self.output_path
            print(f"Audio saved to: {self.output_path}") # Debug print

        except ImportError:
            st.error("SoundFile library not installed. Cannot save audio.")
        except Exception as e:
            st.error(f"Error saving audio: {str(e)}")

    @property
    def recording_duration(self) -> float:
        """Get the current recording duration in seconds"""
        if self.start_time is None:
            return 0
        if self.stopped or self.recording_complete:
            # Calculate duration based on buffer if stopped/completed
            total_samples = sum(len(chunk) for chunk in self.audio_buffer)
            return total_samples / self.sample_rate
        return time.time() - self.start_time


def audio_recorder_ui(
    key: str = "webrtc_recorder",
    title: str = "Audio Recorder",
    description: str = "Record audio for transcription or analysis",
    durations: List[int] = [30, 60, 120, 300],
    show_description: bool = True,
    show_playback: bool = True
) -> Optional[str]:
    """
    Display a WebRTC-based audio recorder widget

    Args:
        key: Unique key for the widget
        title: Title to display above the recorder
        description: Description text
        durations: List of recording duration options in seconds
        show_description: Whether to show the description
        show_playback: Whether to show audio playback after recording

    Returns:
        Base64-encoded audio data if recording is complete, None otherwise
    """
    # Session state initialization
    data_key = f"{key}_data"
    file_path_key = f"{key}_file_path"
    duration_key = f"{key}_duration"
    processor_key = f"{key}_processor"

    if data_key not in st.session_state:
        st.session_state[data_key] = None
    if file_path_key not in st.session_state:
        st.session_state[file_path_key] = None
    if duration_key not in st.session_state:
        st.session_state[duration_key] = durations[0]
    # Initialize processor only if needed
    if processor_key not in st.session_state or st.session_state[processor_key] is None:
        st.session_state[processor_key] = AudioProcessor(max_duration=st.session_state[duration_key])

    # Display title and description
    st.subheader(title)
    if show_description:
        st.write(description)

    # Duration selector
    selected_duration = st.select_slider(
        "Recording duration (seconds)",
        options=durations,
        value=st.session_state[duration_key],
        key=f"{key}_duration_slider"
    )

    # Update session state and processor if duration changed
    if selected_duration != st.session_state[duration_key]:
        st.session_state[duration_key] = selected_duration
        # Recreate processor with new duration if it exists or if state is clear
        st.session_state[processor_key] = AudioProcessor(max_duration=selected_duration)
        st.session_state[data_key] = None # Clear previous data on duration change
        st.session_state[file_path_key] = None
        st.rerun()

    # Create columns for controls
    col1, col2 = st.columns([3, 1]) # Give more space to the streamer

    # WebRTC audio recorder in first column
    with col1:
        # Make sure processor exists
        if processor_key not in st.session_state or st.session_state[processor_key] is None:
             st.session_state[processor_key] = AudioProcessor(max_duration=st.session_state[duration_key])

        # Create the WebRTC streamer
        try:
            webrtc_ctx = webrtc_streamer(
                key=key, # Use the provided key
                mode=WebRtcMode.SENDONLY,
                audio_processor_factory=lambda: st.session_state[processor_key],
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"audio": True, "video": False},
                # desired_playing_state can control start/stop programmatically if needed
            )

            # Check if streamer is active
            if webrtc_ctx.state.playing:
                processor = st.session_state[processor_key]
                if processor:
                    # Show recording status
                    elapsed = processor.recording_duration
                    st.write(f"Recording... ({elapsed:.1f}s / {selected_duration}s)")
                    progress = min(1.0, elapsed / selected_duration)
                    st.progress(progress)
                else:
                     st.warning("Audio processor not available.")
            else:
                # Streamer is stopped or hasn't started
                processor = st.session_state.get(processor_key)
                if processor and processor.audio_buffer and not processor.output_file:
                     # If stopped and audio exists but not saved yet, attempt saving
                     processor.stop()

                if processor and processor.output_file and not st.session_state[data_key]:
                    # If file path exists but data not in session state, load it
                    if os.path.exists(processor.output_file):
                         st.session_state[file_path_key] = processor.output_file
                         try:
                             with open(processor.output_file, "rb") as f:
                                 audio_bytes = f.read()
                                 st.session_state[data_key] = base64.b64encode(audio_bytes).decode("utf-8")
                             st.success("Recording complete!")
                         except Exception as e:
                             st.error(f"Error reading saved audio file: {e}")
                    else:
                         st.warning("Previously saved audio file not found.")
                         st.session_state[file_path_key] = None # Clear invalid path

        except Exception as e:
             st.error(f"Error initializing WebRTC streamer: {e}")
             # Fallback or provide guidance

    # Controls for recorded audio in second column
    with col2:
        # Reset button
        if st.button("Reset Recording", key=f"{key}_reset"):
            # Stop the current processor if it exists and is running
            processor = st.session_state.get(processor_key)
            if processor:
                 processor.stop() # Ensure it stops
                 if processor.output_path and os.path.exists(processor.output_path):
                      try:
                          os.remove(processor.output_path)
                          print(f"Deleted temp file: {processor.output_path}")
                      except OSError as e:
                          print(f"Error deleting temp file {processor.output_path}: {e}")

            # Clear session state
            st.session_state[data_key] = None
            st.session_state[file_path_key] = None
            st.session_state[processor_key] = None # Force re-creation

            st.rerun()

    # Display recorded audio playback below columns
    if show_playback and st.session_state.get(file_path_key):
        try:
            st.audio(st.session_state[file_path_key])
        except Exception as e:
            st.error(f"Could not play audio file: {e}")
            # Potentially clear state if file is corrupted/unreadable
            st.session_state[data_key] = None
            st.session_state[file_path_key] = None


    # Return base64-encoded audio data
    return st.session_state.get(data_key)
