import requests
import os

def call_firebase_function(function_name, payload):
    """
    Call a Firebase Function with the given payload.

    Args:
        function_name: The name of the Firebase Function to call.
        payload: The JSON payload to send to the function.

    Returns:
        The response from the Firebase Function.
    """
    firebase_url = os.environ.get("FIREBASE_FUNCTION_URL")
    if not firebase_url:
        raise ValueError("FIREBASE_FUNCTION_URL environment variable not set.")

    url = f"{firebase_url}/{function_name}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error calling Firebase Function: {str(e)}")

# Example usage
def fetch_rag_response(prompt, pdf_url=None):
    """
    Fetch a RAG (Retrieval-Augmented Generation) response from Firebase.

    Args:
        prompt: The user's input prompt.
        pdf_url: Optional URL to a PDF for context.

    Returns:
        The RAG response from Firebase.
    """
    payload = {"message": prompt}
    if pdf_url:
        payload["pdfUrl"] = pdf_url

    return call_firebase_function("chatWithPDF", payload)