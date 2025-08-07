#!/usr/bin/env python3
"""
Omi Python SDK Setup Script
Complete setup wizard for the Omi Python SDK
"""

import os
import sys
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_dependencies():
    """Check if required dependencies can be imported"""
    dependencies = [
        ("asyncio", "asyncio"),
        ("bleak", "bleak"),
        ("websockets", "websockets"),
        ("httpx", "httpx"),
    ]
    
    missing = []
    
    for name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {name} available")
        except ImportError:
            print(f"❌ {name} missing")
            missing.append(name)
    
    if missing:
        print("\n💡 Install missing dependencies with:")
        print("pip install -r requirements.txt")
        return False
    
    return True


def setup_environment():
    """Setup environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("💡 Edit .env file with your API keys:")
        print("   - DEEPGRAM_API_KEY (required)")
        print("   - OMI_API_KEY (optional, for MCP storage)")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def check_opus_dll():
    """Check if libopus-0.dll is available (Windows only)"""
    if os.name != 'nt':  # Not Windows
        print("ℹ️  Not Windows - libopus-0.dll not needed")
        return True
    
    dll_path = Path("libopus-0.dll")
    
    if dll_path.exists():
        # Check if it's a real DLL (not placeholder)
        size = dll_path.stat().st_size
        if size < 1000:  # Likely a placeholder
            print("⚠️  libopus-0.dll exists but appears to be a placeholder")
            print("💡 Run install_opus_dll.py to set it up properly")
            return True
        else:
            print("✅ libopus-0.dll found and appears valid")
            return True
    else:
        print("❌ libopus-0.dll not found")
        print("💡 Run install_opus_dll.py to download it")
        return False


def check_bluetooth():
    """Check if Bluetooth is available"""
    try:
        import bleak
        print("✅ Bluetooth support available")
        return True
    except ImportError:
        print("❌ Bluetooth support missing (bleak package)")
        return False


def validate_config():
    """Validate the current configuration"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  No .env file found")
        return False
    
    # Basic validation
    has_deepgram = False
    has_omi = False
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
            if 'DEEPGRAM_API_KEY=' in content and 'your_deepgram_api_key_here' not in content:
                has_deepgram = True
            if 'OMI_API_KEY=' in content and 'your_omi_api_key_here' not in content:
                has_omi = True
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        return False
    
    if has_deepgram:
        print("✅ Deepgram API key configured")
    else:
        print("⚠️  Deepgram API key not configured")
    
    if has_omi:
        print("✅ Omi API key configured")
    else:
        print("⚠️  Omi API key not configured (will use local storage)")
    
    return has_deepgram  # At minimum, need Deepgram key


def main():
    """Run the complete setup wizard"""
    print("🚀 Omi Python SDK Setup Wizard")
    print("=" * 40)
    
    success = True
    
    # Check Python version
    print("\n1️⃣  Checking Python version...")
    if not check_python_version():
        success = False
    
    # Check dependencies
    print("\n2️⃣  Checking dependencies...")
    if not check_dependencies():
        success = False
    
    # Setup environment
    print("\n3️⃣  Setting up environment...")
    if not setup_environment():
        success = False
    
    # Check Opus DLL (Windows)
    print("\n4️⃣  Checking Opus DLL...")
    check_opus_dll()  # Non-blocking
    
    # Check Bluetooth
    print("\n5️⃣  Checking Bluetooth support...")
    check_bluetooth()  # Non-blocking
    
    # Validate final config
    print("\n6️⃣  Validating configuration...")
    config_valid = validate_config()
    
    # Summary
    print("\n" + "=" * 40)
    if success and config_valid:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Edit your .env file with real API keys")
        print("2. Update OMI_MAC in main.py with your device's MAC address")
        print("3. Run: python main.py")
    elif success:
        print("⚠️  Setup mostly complete!")
        print("\n📋 Required actions:")
        print("1. Edit your .env file with real API keys")
        print("2. Update OMI_MAC in main.py with your device's MAC address")
        print("3. Run: python main.py")
    else:
        print("❌ Setup incomplete!")
        print("\n📋 Required actions:")
        print("1. Fix the issues listed above")
        print("2. Run this setup script again")
    
    print("\n💡 For help, see README.md or OPUS_SETUP.md")


if __name__ == "__main__":
    main()
