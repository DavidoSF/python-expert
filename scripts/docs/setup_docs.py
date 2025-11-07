#!/usr/bin/env python3
"""
Setup script for documentation - works on all platforms
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up documentation environment...")
    
    # Get the project root (two levels up from this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Change to project root for pip install
    original_dir = os.getcwd()
    os.chdir(project_root)
    
    try:
        # Step 1: Install dependencies
        if not run_command("pip install -r requirements.txt", "Installing dependencies"):
            return 1
        
        # Step 2: Change to docs directory
        os.chdir(script_dir)
        
        # Step 3: Build documentation
        if os.name == 'nt':  # Windows
            build_cmd = "make.bat html"
        else:  # Unix-like systems
            build_cmd = "make html"
            
        if not run_command(build_cmd, "Building documentation"):
            return 1
        
        # Step 4: Success message
        print("\n🎉 Documentation setup complete!")
        print("\n📖 To view the documentation:")
        print("   Option 1: Open _build/html/index.html in your browser")
        print("   Option 2: Run 'python -m http.server 8000' in _build/html/ directory")
        print("            Then open http://localhost:8000")
        
        return 0
        
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    sys.exit(main())