import os
import sys

from fastapi import FastAPI  # fastapi ^0.95.0
import uvicorn  # uvicorn ^0.22.0

from app.main import app  # Import the main FastAPI application instance

# Define WSGI application instance
application = app