"""
Vercel serverless function entry point for SIDMS Backend
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app
from app import app

# Vercel expects a handler function
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda status, headers: None)

# For local testing
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
