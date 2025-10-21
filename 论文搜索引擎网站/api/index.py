"""
Vercel Serverless Function for FastAPI
This file handles API requests for Vercel deployment
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the FastAPI app from main.py
from main import app

# Import Mangum for AWS Lambda compatibility
from mangum import Mangum

# Create handler for Vercel
handler = Mangum(app)

# Vercel expects the handler to be named 'app'
app = handler