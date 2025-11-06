#!/usr/bin/env python3
"""
Simple script to build Sphinx documentation
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """Build the documentation"""
    docs_dir = Path(__file__).parent
    source_dir = docs_dir / "source"
    build_dir = docs_dir / "_build" / "html"
    
    print("Building Sphinx documentation...")
    print(f"Source: {source_dir}")
    print(f"Build: {build_dir}")
    
    # Clean previous build
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
        print("Cleaned previous build")
    
    # Build documentation
    cmd = [
        "sphinx-build",
        "-b", "html",
        "-W",  # Turn warnings into errors
        str(source_dir),
        str(build_dir)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Documentation built successfully!")
        print(f"Output: {build_dir}/index.html")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())