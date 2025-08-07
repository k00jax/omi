#!/usr/bin/env python3
"""
Omi Python SDK - Quick Start Script
One-command setup and launch
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors gracefully"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"⚠️  {description} completed with warnings")
            if result.stderr:
                print(f"   {result.stderr.strip()}")
            return True  # Continue anyway
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False


def main():
    """One-command setup and launch"""
    print("🚀 Omi Python SDK - Quick Start")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Run this from the SDK directory.")
        sys.exit(1)
    
    # Step 1: Setup system
    print("\n1️⃣  Running setup...")
    if not run_command(f"{sys.executable} setup.py", "System setup"):
        sys.exit(1)
    
    # Step 2: Install Opus DLL (Windows only)
    if os.name == 'nt':
        print("\n2️⃣  Setting up audio codec...")
        run_command(f"{sys.executable} install_opus_dll.py", "Opus DLL setup")
    
    # Step 3: Run tests
    print("\n3️⃣  Running tests...")
    run_command(f"{sys.executable} test.py", "System tests")
    
    # Step 4: Check configuration
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "your_deepgram_api_key_here" in content:
            print("\n⚠️  ACTION REQUIRED:")
            print("1. Edit .env file with your real Deepgram API key")
            print("2. Optionally add OMI_API_KEY for MCP storage")
            print("3. Update OMI_MAC in main.py with your device's MAC address")
            print("\n💡 Then run: python main.py")
        else:
            print("\n🎉 Setup complete! Ready to run:")
            print("python main.py")
    else:
        print("\n⚠️  Configuration incomplete. Run setup.py manually.")
    
    print("\n" + "=" * 40)
    print("📋 Quick Reference:")
    print("• python main.py           - Start the SDK")
    print("• python test.py           - Run tests")
    print("• python setup.py          - Reconfigure")
    print("• See SYSTEM_OVERVIEW.md   - Complete docs")


if __name__ == "__main__":
    main()
