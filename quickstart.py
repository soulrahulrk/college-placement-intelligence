"""
Quick Start Script for College Placement Intelligence Agent
Run this to set up and launch everything automatically
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(command, shell=True, capture_output=False)
    
    if result.returncode != 0:
        print(f"❌ Error executing: {description}")
        return False
    
    print(f"✅ {description} - Complete!")
    return True

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  🎓 College Placement Intelligence Agent - Quick Start   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check Python version
    print(f"\n🐍 Python Version: {sys.version}")
    
    # Step 2: Install dependencies
    if not run_command(
        "pip install -r requirements.txt",
        "Installing dependencies"
    ):
        return
    
    # Step 3: Generate synthetic data
    if not run_command(
        "python data_engine.py",
        "Generating synthetic data (students, jobs, logs)"
    ):
        return
    
    # Step 4: Test intelligence engine
    if not run_command(
        "python intelligence.py",
        "Testing intelligence engine"
    ):
        return
    
    # Step 5: Launch Streamlit
    print(f"\n{'='*60}")
    print("🚀 Launching Streamlit Dashboard...")
    print("📍 The app will open in your browser at http://localhost:8501")
    print("📍 Press Ctrl+C to stop the server")
    print(f"{'='*60}\n")
    
    subprocess.run("streamlit run app.py", shell=True)

if __name__ == "__main__":
    main()
