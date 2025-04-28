#!/usr/bin/env python
import os
import subprocess
import sys

def main():
    """Launch the Streamlit dashboard."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Run streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", "src/app.py"]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
