#!/usr/bin/env python
import os
import subprocess
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Launch the Streamlit dashboard."""
    # Print information
    print("Starting Daily Routine Dashboard...")
    print(f"Project root: {project_root}")
    
    # Get the virtual environment Python
    venv_python = os.path.join(project_root, '.venv', 'bin', 'python')
    
    if not os.path.exists(venv_python):
        print(f"Error: Virtual environment Python not found at {venv_python}")
        print("Please ensure you've created and activated the virtual environment:")
        print("  uv venv")
        print("  source .venv/bin/activate")
        print("  uv pip install -e .")
        return
    
    # Get the streamlit executable from the virtual environment
    venv_streamlit = os.path.join(project_root, '.venv', 'bin', 'streamlit')
    
    if not os.path.exists(venv_streamlit):
        print(f"Error: Streamlit not found at {venv_streamlit}")
        print("Please ensure streamlit is installed in the virtual environment:")
        print("  uv pip install -e .")
        return
    
    # Change to the script directory
    os.chdir(project_root)
    
    # Run streamlit from the virtual environment
    app_path = os.path.join(project_root, 'src', 'app.py')
    cmd = [venv_streamlit, "run", app_path]
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
