#!/usr/bin/env python3
"""
Demo script to test transcript UI with simulated transcripts
This bypasses the Opus decoding issue and shows how the UI works
"""

import asyncio
import os
import sys
from transcript_ui import TranscriptWindow
from memory import init_memory_storage, process_transcript_for_memory, cleanup_memory_storage
from env_config import setup_environment

async def demo_transcripts():
    """Demo the transcript UI with simulated transcripts"""
    
    # Setup environment
    print("🔧 Setting up environment...")
    setup_environment()
    
    # Initialize memory storage
    print("🧠 Initializing memory storage...")
    omi_key = os.getenv("OMI_API_KEY", "demo_key")
    user_id = os.getenv("USER_ID", "demo_user")
    init_memory_storage(omi_key, user_id=user_id)
    
    # Create UI
    print("🖥️ Starting transcript UI demo...")
    ui = TranscriptWindow("🎧 Omi Live Transcript - DEMO MODE")
    
    # Wait for UI to initialize
    await asyncio.sleep(2)
    
    # Demo sequence
    demo_phrases = [
        "Hello, this is a test of the Omi transcript system",
        "The audio decoding is working and data is flowing properly",
        "Remember to buy groceries tomorrow",  # Should trigger memory
        "The weather looks nice today",
        "Note that this is an important meeting",  # Should trigger memory
        "I need to call my doctor about the appointment",
        "The real-time transcript is updating correctly",
        "This is a demonstration of the memory creation system",
        "Add this to my todo list",  # Should trigger memory
        "Everything seems to be working perfectly"
    ]
    
    ui.update_status("🎤 DEMO MODE - Simulating live transcripts...")
    
    print("🎭 Starting demo sequence...")
    
    for i, phrase in enumerate(demo_phrases):
        if not ui.is_running():
            print("🚪 UI closed, stopping demo")
            break
            
        print(f"📝 Demo phrase {i+1}: {phrase}")
        
        # Update transcript in UI
        ui.update_transcript(phrase)
        
        # Process for memory creation
        try:
            memory_created, category = await process_transcript_for_memory(phrase, {"demo": True})
            if memory_created and category:
                print(f"📌 Memory created: {category}")
                ui.update_memory(category, phrase)
            else:
                print("ℹ️  No hot phrase detected")
        except Exception as e:
            print(f"Memory processing error: {e}")
        
        # Wait between phrases
        await asyncio.sleep(3)
    
    print("✅ Demo completed!")
    ui.update_status("✅ Demo completed - UI fully functional!")
    
    # Keep UI open until user closes it
    while ui.is_running():
        await asyncio.sleep(1)
    
    print("🧹 Cleaning up...")
    await cleanup_memory_storage()

async def main():
    """Run the demo"""
    print("🚀 Omi Transcript UI Demo")
    print("=" * 40)
    print("This demo shows how the transcript UI works")
    print("with simulated transcripts while we fix the Opus decoder.")
    print("")
    print("You should see:")
    print("- Real-time transcript updates")
    print("- Memory creation for key phrases")
    print("- Status updates")
    print("- Professional UI with controls")
    print("=" * 40)
    
    try:
        await demo_transcripts()
    except KeyboardInterrupt:
        print("🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    print("Demo finished!")

if __name__ == "__main__":
    asyncio.run(main())
