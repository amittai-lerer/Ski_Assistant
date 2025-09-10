#!/usr/bin/env python3
"""
Quick launcher for SkiTrip Assistant Streamlit UI

Usage:
    python run_streamlit.py

This will start the Streamlit web interface for the SkiTrip Assistant.
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit app."""
    print("🏂 Starting SkiTrip Assistant Streamlit UI...")

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the Streamlit app
    app_path = os.path.join(script_dir, "app", "streamlit_app.py")

    # Check if the app file exists
    if not os.path.exists(app_path):
        print(f"❌ Error: Streamlit app not found at {app_path}")
        sys.exit(1)

    # Launch Streamlit
    try:
        cmd = [sys.executable, "-m", "streamlit", "run", app_path]
        print(f"🚀 Running: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=script_dir)
    except KeyboardInterrupt:
        print("\n👋 Streamlit UI stopped by user")
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
