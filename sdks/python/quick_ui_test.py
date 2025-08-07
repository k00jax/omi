#!/usr/bin/env python3
"""
Quick UI test - shows transcripts immediately so you can see the window working
"""

import asyncio
import os
from transcript_ui import TranscriptWindow
from env_config import setup_environment

async def quick_ui_test():
    """Test the UI with immediate transcripts"""
    
    print("🔧 Setting up environment...")
    setup_environment()
    
    print("🖥️ Starting transcript UI test...")
    ui = TranscriptWindow("🧪 Quick UI Test")
    
    # Wait a moment for UI to initialize
    await asyncio.sleep(1)
    
    print("📝 Adding test transcripts immediately...")
    
    # Show transcripts right away
    test_transcripts = [
        "Hello! This is transcript number 1",
        "This is transcript number 2 - testing the UI",
        "Transcript 3 - the system is working!",
        "Remember to fix the Opus decoder",  # Should create memory
        "Final test transcript - UI is functional!"
    ]
    
    ui.update_status("🧪 Running UI test...")
    
    for i, transcript in enumerate(test_transcripts):
        if not ui.is_running():
            print("❌ UI closed early")
            break
            
        print(f"📝 Adding transcript {i+1}: {transcript}")
        ui.update_transcript(transcript)
        
        if "fix" in transcript.lower() or "remember" in transcript.lower():
            print("📌 Test memory creation")
            ui.update_memory("note", transcript)
        
        await asyncio.sleep(2)  # 2 seconds between transcripts
    
    print("✅ Test transcripts added! Keep window open to see them.")
    ui.update_status("✅ Test completed - UI is working!")
    
    # Keep running until user closes window
    while ui.is_running():
        await asyncio.sleep(1)
    
    print("✅ UI test completed!")

if __name__ == "__main__":
    print("🚀 Quick UI Test")
    print("=" * 30)
    print("This will immediately show test transcripts in the UI")
    print("Keep the window open to see them appear!")
    print("=" * 30)
    
    asyncio.run(quick_ui_test())
