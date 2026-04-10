#!/usr/bin/env python3
"""Backend server startup script"""
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import uvicorn and run
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
