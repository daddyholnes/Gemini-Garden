"""
WSGI server wrapper for Streamlit application with security middleware.
This allows us to add security headers to Streamlit responses.
"""
import os
import streamlit.web.bootstrap as bootstrap
from utils.security_middleware import apply_security_middleware
import streamlit as st

# Set environment variables
os.environ["BYPASS_STATE_CHECK"] = "true"  # Enable this to bypass OAuth state check for now

def run_streamlit():
    """Run the Streamlit app with security middleware applied."""
    # Get the path to the Streamlit app
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'app.py')
    
    # Set flag and arguments
    flag_options = {
        'server.enableCORS': False,  # Disable CORS to ensure security headers work
        'server.enableXsrfProtection': True,  # Enable XSRF protection
        'server.enableWebsocketCompression': True,
        'server.headless': True,  # Run in headless mode
        'browser.serverAddress': 'ai-chat-studio.dartopia.uk',  # Set correct domain
        'browser.gatherUsageStats': False,  # Don't gather usage stats
    }
    
    args = []
    for key, value in flag_options.items():
        if isinstance(value, bool):
            args.extend(['--' + key, str(value).lower()])
        else:
            args.extend(['--' + key, str(value)])
    
    # Run the Streamlit app with our security middleware
    bootstrap.run(filename, '', args, flag_options=flag_options)

if __name__ == "__main__":
    run_streamlit()