#!/usr/bin/env python3
"""
Build Script for SMS Conductor Database Viewer
Creates Windows EXE with PyInstaller

Usage:
    python build_exe.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("=" * 60)
    print("SMS Conductor Database Viewer - Build Script")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("ERROR: PyInstaller not found!")
        print("\nInstalling PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully")
    
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    spec_file = project_root / "SMSConductorDB.spec"
    
    # Clean old builds
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    
    if dist_dir.exists():
        print("\nCleaning old dist directory...")
        shutil.rmtree(dist_dir)
    
    if build_dir.exists():
        print("Cleaning old build directory...")
        shutil.rmtree(build_dir)
    
    # Build with PyInstaller
    print("\nBuilding EXE...")
    print(f"Using spec file: {spec_file}")
    
    # Use python -m PyInstaller to avoid PATH issues
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]
    
    print(f"\nCommand: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=str(project_root))
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"\nOutput: {dist_dir / 'SMSConductorDB'}")
        print("\nYou can now:")
        print("  1. Run: dist\\SMSConductorDB\\SMSConductorDB.exe")
        print("  2. Zip the entire 'SMSConductorDB' folder for distribution")
        print("\n")
    else:
        print("\n" + "=" * 60)
        print("BUILD FAILED!")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()

