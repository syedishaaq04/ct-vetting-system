#!/usr/bin/env python3
"""
Startup script for CT Scan Vetting System
MVP for College Tech Expo
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import transformers
        import groq
        print("Backend dependencies: OK")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_node_npm():
    """Check if Node.js and npm are available"""
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
        print("Node.js/npm: OK")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Node.js/npm not found. Please install Node.js for the frontend.")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("Starting FastAPI backend...")
    try:
        process = subprocess.Popen([sys.executable, 'api.py'], 
                                  cwd=Path(__file__).parent)
        return process
    except Exception as e:
        print(f"Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the React frontend"""
    print("Starting React frontend...")
    frontend_dir = Path(__file__).parent / 'frontend'
    try:
        process = subprocess.Popen(['npm', 'start'], 
                                  cwd=frontend_dir)
        return process
    except Exception as e:
        print(f"Failed to start frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("CT Scan Vetting System - Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    if not check_node_npm():
        print("Continuing with backend only...")
    
    print("\nStarting services...")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("Failed to start backend. Exiting.")
        return
    
    # Wait for backend to start
    print("Waiting for backend to initialize...")
    time.sleep(5)
    
    # Start frontend if available
    frontend_process = None
    if check_node_npm():
        frontend_process = start_frontend()
    
    print("\n" + "=" * 40)
    print("Services are starting up...")
    print("\nAvailable at:")
    print("- Backend API: http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")
    if frontend_process:
        print("- Frontend: http://localhost:3000")
        print("\nOpening frontend in browser...")
        time.sleep(3)
        webbrowser.open('http://localhost:3000')
    else:
        print("\nOpening API docs in browser...")
        time.sleep(2)
        webbrowser.open('http://localhost:8000/docs')
    
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("Services stopped.")

if __name__ == "__main__":
    main()
