import os
import sys
import requests
import json
from typing import List, Dict, Any, Optional, Generator
import base64
from PIL import Image
import io

# --- Model Definitions ---

SUPPORTED_MODELS = {
    # Gemini Models (using google.generativeai)
    "Gemini 1.5 Pro (Google)": {"api": "gemini", "model_name": "gemini-1.5-pro"},
    "Gemini 1.5 Flash (Google)": {"api": "gemini", "model_name": "gemini-1.5-flash"},
    # Add other Gemini models from the original GEMINI_MODELS dict as needed
    # "Gemini 2.5 Pro Preview (Google)": {"api": "gemini", "model_name": "gemini-2.5-pro-preview-03-25"}, # Example if needed
    "Gemini 2.0 Flash (Google)": {"api": "gemini", "model_name": "gemini-2.0-flash"},

    # Anthropic Models
    "Claude 3.5 Sonnet (Anthropic)": {"api": "anthropic", "model_name": "claude-3-5-sonnet-20241022"},
    # Add other Claude models if you have access or they are released
    # "Claude 3 Opus (Anthropic)": {"api": "anthropic", "model_name": "claude-3-opus-20240229"}, # Example

    # OpenAI Models
    "GPT-4o (OpenAI)": {"api": "openai", "model_name": "gpt-4o"},
    "GPT-4 Turbo (OpenAI)": {"api": "openai", "model_name": "gpt-4-turbo"},
    "GPT-3.5 Turbo (OpenAI)": {"api": "openai", "model_name": "gpt-3.5-turbo"},

    # Perplexity Models
    "Perplexity Online 70B (Perplexity)": {"api": "perplexity", "model_name": "pplx-70b-online"},
    "Perplexity Chat 70B (Perplexity)": {"api": "perplexity", "model_name": "pplx-70b-chat"},
    # Add other Perplexity models if needed
}

# --- Central API Router --- #
# Note: This router currently returns the full response. We'll adapt it for streaming.
def generate_chat_response(
    selected_model_key: str,
    prompt: str,
    message_history: List[Dict[str, str]],
    image_data: Optional[str] = None,
    audio_data: Optional[str] = None,
    temperature: float = 0.7,
    stream: bool = False # Add stream parameter
) -> Generator[str, None, None] | str:
    """
    Generates a chat response (optionally streaming) using the specified model.

    Args:
        selected_model_key: The key corresponding to the model in SUPPORTED_MODELS.
        prompt: The user's input prompt.
        message_history: Previous message history.
        image_data: Optional base64 encoded image data.
        audio_data: Optional base64 encoded audio data.
        temperature: Temperature for response generation.
        stream: If True, yields chunks of the response.

    Returns:
        A generator yielding response chunks if stream=True, otherwise the full response text.
        Returns an error message string on failure.
    """
    if selected_model_key not in SUPPORTED_MODELS:
        error_msg = f"Error: Model '{selected_model_key}' not found in supported models."
        if stream:
            yield error_msg
            return
        else:
            return error_msg

    model_info = SUPPORTED_MODELS[selected_model_key]
    api_type = model_info["api"]
    model_name = model_info["model_name"]

    try:
        if api_type == "gemini":
            # Call the Gemini function, passing the stream flag
            return get_gemini_response(
                prompt=prompt,
                message_history=message_history,
                image_data=image_data,
                audio_data=audio_data,
                temperature=temperature,
                model_name=model_name,
                stream=stream # Pass the stream flag
            )
        # --- Add streaming logic for other APIs later if needed --- 
        elif api_type == "anthropic":
            if stream:
                 # Placeholder: Anthropic streaming needs separate implementation
                 yield "Streaming not yet implemented for Anthropic."
                 return
            return get_anthropic_response(
                prompt=prompt,
                message_history=message_history,
                model_name=model_name
            )
        elif api_type == "openai":
            if stream:
                # Placeholder: OpenAI streaming needs separate implementation
                yield "Streaming not yet implemented for OpenAI."
                return
            return get_openai_response(
                prompt=prompt,
                message_history=message_history,
                model_name=model_name
            )
        elif api_type == "perplexity":
            if stream:
                 # Placeholder: Perplexity streaming needs separate implementation
                 yield "Streaming not yet implemented for Perplexity."
                 return
            return get_perplexity_response(
                prompt=prompt,
                message_history=message_history,
                temperature=temperature,
                model_name=model_name
            )
        else:
            error_msg = f"Error: API type '{api_type}' is not recognized."
            if stream:
                yield error_msg
                return
            else:
                return error_msg

    except Exception as e:
        error_msg = f"Error generating response with {selected_model_key}: {str(e)}"
        if stream:
             yield error_msg
             return
        else:
            return error_msg

# --- Individual API Functions --- #

# Gemini API (Modified to handle streaming)
def get_gemini_response(
    prompt: str,
    message_history: List[Dict[str, str]],
    image_data: Optional[str] = None,
    audio_data: Optional[str] = None,
    temperature: float = 0.7,
    model_name: str = "gemini-1.5-pro",
    stream: bool = False # Add stream parameter
) -> Generator[str, None, None] | str:
    """
    Get a response from the Gemini AI model (optionally streaming).
    Handles text, image, audio.
    """
    try:
        import google.generativeai as genai

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")

        genai.configure(api_key=api_key)

        # Format history
        formatted_history = []
        for message in message_history:
             role = "user" if message["role"] == "user" else "model"
             # Basic text history for now
             if isinstance(message["content"], str):
                 formatted_history.append({"role": role, "parts": [message["content"]]})
             # TODO: Add multimodal history formatting if needed

        model = genai.GenerativeModel(
            model_name,
            generation_config=genai.types.GenerationConfig(temperature=temperature)
        )

        # Prepare content parts for the current prompt
        content_parts = []
        if image_data:
            try:
                image_bytes = base64.b64decode(image_data)
                img = Image.open(io.BytesIO(image_bytes))
                content_parts.append(img)
            except Exception as e:
                raise ValueError(f"Error processing image data: {str(e)}")
        if audio_data:
             try:
                 audio_bytes = base64.b64decode(audio_data)
                 # Adjust mime_type based on actual audio format
                 content_parts.append({"mime_type": "audio/wav", "data": audio_bytes})
             except Exception as e:
                 raise ValueError(f"Error processing audio data: {str(e)}")

        content_parts.append(prompt)

        # --- Streaming Logic --- 
        if stream:
            # Use generate_content with stream=True
            # Note: History handling with multimodal + streaming can be complex.
            # For simplicity, let's pass history for text-only, but not with images/audio yet.
            if image_data or audio_data:
                 # Multimodal streaming often doesn't use chat history directly
                 response_stream = model.generate_content(content_parts, stream=True)
            else:
                 # Text-only streaming can use chat history
                 chat = model.start_chat(history=formatted_history)
                 response_stream = chat.send_message(prompt, stream=True)

            # Define a generator function to yield text chunks
            def stream_generator():
                try:
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                except Exception as e:
                    yield f"Error during Gemini stream: {str(e)}"
            return stream_generator()

        # --- Non-Streaming Logic --- 
        else:
            if image_data or audio_data:
                 # Single turn generation for multimodal
                 response = model.generate_content(content_parts)
            else:
                 # Use chat session for text-only
                 chat = model.start_chat(history=formatted_history)
                 response = chat.send_message(prompt)
            return response.text

    except Exception as e:
        error_message = f"Error with Gemini API ({model_name}): {str(e)}"
        # If streaming was requested, yield the error; otherwise, return it.
        if stream:
            def error_stream(): yield error_message
            return error_stream()
        else:
            return error_message


# OpenAI API (Streaming NOT implemented yet)
def get_openai_response(prompt: str, message_history: List[Dict[str, str]], model_name="gpt-4o") -> str:
    """ Get a response from the OpenAI GPT model. """
    try:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable."
        client = OpenAI(api_key=api_key)
        formatted_messages = [{"role": m["role"], "content": m["content"]} for m in message_history]
        formatted_messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=model_name,
            messages=formatted_messages,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error with OpenAI API ({model_name}): {str(e)}"


# Anthropic API (Streaming NOT implemented yet)
def get_anthropic_response(prompt: str, message_history: List[Dict[str, str]], model_name="claude-3-5-sonnet-20241022") -> str:
    """ Get a response from the Anthropic Claude model. """
    try:
        from anthropic import Anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "Error: Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
        client = Anthropic(api_key=api_key)
        formatted_messages = []
        for message in message_history:
             role = "user" if message["role"] == "user" else "assistant"
             content = message.get("content", "")
             if isinstance(content, str):
                 formatted_messages.append({"role": role, "content": content})

        formatted_messages.append({"role": "user", "content": prompt})

        response = client.messages.create(
            model=model_name,
            messages=formatted_messages,
            max_tokens=1500
        )
        return response.content[0].text
    except Exception as e:
        return f"Error with Anthropic API ({model_name}): {str(e)}"


# Perplexity API (Streaming NOT implemented yet)
def get_perplexity_response(prompt: str, message_history: List[Dict[str, str]], temperature=0.7, model_name="pplx-70b-online") -> str:
    """ Get a response from the Perplexity API. """
    try:
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if not api_key:
            return "Error: Perplexity API key not found. Set PERPLEXITY_API_KEY environment variable."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        formatted_messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        for message in message_history:
            role = "user" if message["role"] == "user" else "assistant"
            content = message.get("content", "")
            if isinstance(content, str):
                formatted_messages.append({"role": role, "content": content})

        formatted_messages.append({"role": "user", "content": prompt})

        data = {
            "model": model_name,
            "messages": formatted_messages,
            "temperature": temperature,
        }

        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
         error_details = e.response.text if e.response else "No response details"
         return f"Error with Perplexity API request ({model_name}): {str(e)} - {error_details}"
    except Exception as e:
        return f"Error with Perplexity API ({model_name}): {str(e)}"

