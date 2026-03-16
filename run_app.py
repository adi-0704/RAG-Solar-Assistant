import subprocess
import os
import sys

def run():
    print("Starting Solar RAG Chatbot...")
    
    # Run uvicorn in a separate process
    backend_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"])
    
    # Run streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])
    except KeyboardInterrupt:
        print("Stopping application...")
    finally:
        backend_process.terminate()

if __name__ == "__main__":
    run()
