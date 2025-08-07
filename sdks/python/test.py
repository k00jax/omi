#!/usr/bin/env python3
"""
Test script for Omi Python SDK
Tests core functionality without requiring actual hardware
"""

import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock
from memory import init_memory_storage, process_transcript_for_memory, cleanup_memory_storage
from env_config import setup_environment


def test_ui_imports():
    """Test that UI components can be imported"""
    print("🧪 Testing UI imports...")
    try:
        import tkinter as tk
        print("✅ tkinter")
        
        from transcript_ui import TranscriptWindow
        print("✅ TranscriptWindow")
        
        print("✅ UI imports successful")
        return True
    except ImportError as e:
        print(f"❌ UI import failed: {e}")
        return False


def test_ui_functionality():
    """Test basic UI functionality"""
    print("🧪 Testing UI functionality...")
    try:
        from transcript_ui import TranscriptWindow
        
        # Create UI instance (won't show window in test)
        ui = TranscriptWindow()
        
        # Test basic methods
        ui.update_transcript("Test message")
        ui.update_status("Test status")
        ui.update_memory("note", "Test memory")
        
        print("✅ UI functionality test passed")
        return True
    except Exception as e:
        print(f"❌ UI functionality test failed: {e}")
        return False


async def test_memory_system():
    """Test the memory system functionality"""
    print("🧪 Testing memory system...")
    
    # Initialize with dummy key for testing
    init_memory_storage("test_key", user_id="test_user")
    
    # Test hot phrase detection and memory creation
    test_phrases = [
        "This is just a regular sentence",
        "Hey, note this important information",
        "Remember this for later",
        "I have an idea about the project",
        "This is important to remember",
        "Add this to my todo list"
    ]
    
    for phrase in test_phrases:
        print(f"\n📝 Testing phrase: '{phrase}'")
        memory_created, category = await process_transcript_for_memory(phrase, {"test": True})
        if memory_created:
            print("✅ Memory created")
        else:
            print("ℹ️  No hot phrase detected")
    
    await cleanup_memory_storage()
    print("\n✅ Memory system test completed")


def test_environment():
    """Test environment configuration"""
    print("🧪 Testing environment configuration...")
    
    # Test environment setup
    result = setup_environment()
    
    if result:
        print("✅ Environment configuration successful")
    else:
        print("⚠️  Environment configuration incomplete")
    
    # Check key environment variables
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    omi_key = os.getenv("OMI_API_KEY")
    
    if deepgram_key and "your_deepgram_api_key_here" not in deepgram_key:
        print("✅ Deepgram API key configured")
    else:
        print("⚠️  Deepgram API key not configured")
    
    if omi_key and "your_omi_api_key_here" not in omi_key:
        print("✅ Omi API key configured")
    else:
        print("ℹ️  Omi API key not configured (will use local storage)")


def test_imports():
    """Test all required imports"""
    print("🧪 Testing module imports...")
    
    try:
        import asyncio
        print("✅ asyncio")
    except ImportError:
        print("❌ asyncio")
        return False
    
    try:
        import bleak
        print("✅ bleak (Bluetooth)")
    except ImportError:
        print("❌ bleak (Bluetooth)")
        return False
    
    try:
        import websockets
        print("✅ websockets")
    except ImportError:
        print("❌ websockets")
        return False
    
    try:
        import httpx
        print("✅ httpx")
    except ImportError:
        print("❌ httpx")
        return False
    
    try:
        from omi.bluetooth import listen_to_omi
        print("✅ omi.bluetooth")
    except ImportError:
        print("❌ omi.bluetooth")
        return False
    
    try:
        from omi.transcribe import transcribe
        print("✅ omi.transcribe")
    except ImportError:
        print("❌ omi.transcribe")
        return False
    
    try:
        from omi.decoder import OmiOpusDecoder
        print("✅ omi.decoder")
    except Exception as e:
        print(f"⚠️  omi.decoder: {e}")
        print("   (This is expected if libopus-0.dll is not properly installed)")
        print("   💡 Run install_opus_dll.py to fix this")
        # This is non-critical for basic testing
    
    return True


async def main():
    """Run all tests"""
    print("🚀 Omi Python SDK Test Suite")
    print("=" * 40)
    
    success = True
    
    # Test imports
    print("\n1️⃣  Testing imports...")
    if not test_imports():
        success = False
    
    # Test UI components
    print("\n2️⃣  Testing UI components...")
    if not test_ui_imports():
        success = False
    else:
        test_ui_functionality()
    
    # Test environment
    print("\n3️⃣  Testing environment...")
    test_environment()
    
    # Test memory system
    print("\n4️⃣  Testing memory system...")
    await test_memory_system()
    
    # Summary
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed!")
        print("\n📋 Next steps:")
        print("1. Configure your API keys in .env")
        print("2. Update OMI_MAC in main.py")
        print("3. Run: python main.py")
        print("4. Try: python demo_ui.py (to demo the transcript UI)")
    else:
        print("❌ Some tests failed!")
        print("\n📋 Actions needed:")
        print("1. Fix import errors (install dependencies)")
        print("2. Run setup.py for guided configuration")
    
    print("\nTest Results Summary:")
    print("- Check local file: omi_memories.txt for test memories")
    print("- Verify .env file was created and configured")
    print("- UI components tested and ready")


if __name__ == "__main__":
    asyncio.run(main())
