"""
Security middleware for the Streamlit application.
This adds proper security headers to HTTP responses.
"""
from functools import wraps

def add_security_headers(response):
    """
    Add security headers to an HTTP response.
    This function adds various security headers to improve the security posture of the application.
    """
    headers = response.headers

    # Content Security Policy to prevent XSS attacks
    headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://storage.googleapis.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://*.googleapis.com https://*.gstatic.com https://api.openai.com https://api.anthropic.com https://api.perplexity.ai https://*.generativelanguage.googleapis.com wss:"
    )
    
    # X-Content-Type-Options to prevent MIME type sniffing
    headers['X-Content-Type-Options'] = 'nosniff'
    
    # X-Frame-Options to prevent clickjacking
    headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # X-XSS-Protection as an additional layer of XSS protection for older browsers
    headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer-Policy to control how much referrer information should be included with requests
    headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Ensure proper content-type charset values
    if 'Content-Type' in headers:
        content_type = headers['Content-Type']
        if 'text/css' in content_type and 'charset=' not in content_type.lower():
            headers['Content-Type'] = f"{content_type}; charset=utf-8"
        elif 'application/javascript' in content_type and 'charset=' not in content_type.lower():
            headers['Content-Type'] = f"{content_type}; charset=utf-8"
        elif 'application/json' in content_type and 'charset=' not in content_type.lower():
            headers['Content-Type'] = f"{content_type}; charset=utf-8"
    
    # Cache control headers
    headers['Cache-Control'] = 'private, max-age=3600'
    
    # Set secure cookies
    if 'Set-Cookie' in headers:
        cookie = headers['Set-Cookie']
        if 'secure' not in cookie.lower() and 'localhost' not in response.url.lower():
            headers['Set-Cookie'] = f"{cookie}; Secure; HttpOnly; SameSite=Strict"
        elif 'httponly' not in cookie.lower():
            headers['Set-Cookie'] = f"{cookie}; HttpOnly; SameSite=Strict"
    
    return response

def apply_security_middleware(app):
    """
    Apply security middleware to a Flask or WSGI application.
    This function wraps the application's response and adds security headers.
    
    Args:
        app: The Flask or WSGI application to wrap
        
    Returns:
        The wrapped application with security headers
    """
    @wraps(app)
    def middleware(*args, **kwargs):
        response = app(*args, **kwargs)
        return add_security_headers(response)
    return middleware