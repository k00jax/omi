"""
Test script for the Transcript UI
Demonstrates the real-time transcript window with sample data
"""

import asyncio
import time
from transcript_ui import TranscriptWindow

async def demo_transcript_ui():
    """Demo the transcript UI with sample data"""
    print("🚀 Starting Transcript UI Demo...")
    
    # Create the UI window
    ui = TranscriptWindow("🧪 Transcript UI Demo")
    
    # Wait a moment for UI to initialize
    await asyncio.sleep(1)
    
    # Sample transcript data
    sample_transcripts = [
        "Hello, this is a test of the transcript system.",
        "The weather is really nice today.",
        "Note this: Remember to pick up groceries on the way home.",
        "I have an idea about improving our workflow process.",
        "This is important: The meeting has been moved to 3 PM.",
        "Todo: Need to finish the project documentation by Friday.",
        "Let me contact Sarah about the budget meeting.",
        "The system is working perfectly with real-time updates."
    ]
    
    # Status updates
    ui.update_status("🔄 Demo started...")
    await asyncio.sleep(1)
    
    ui.update_status("🔵 Simulating Omi connection...")
    await asyncio.sleep(1)
    
    ui.update_status("🎤 Processing audio stream...")
    await asyncio.sleep(1)
    
    ui.update_status("🟢 Connected and transcribing...")
    
    # Add sample transcripts with delays
    for i, transcript in enumerate(sample_transcripts):
        await asyncio.sleep(2)  # Simulate real-time delay
        
        print(f"📝 Adding transcript: {transcript}")
        ui.update_transcript(transcript)
        
        # Simulate memory creation for certain phrases
        if "note this" in transcript.lower():
            await asyncio.sleep(0.5)
            ui.update_memory("note", transcript)
        elif "idea" in transcript.lower():
            await asyncio.sleep(0.5)
            ui.update_memory("idea", transcript)
        elif "important" in transcript.lower():
            await asyncio.sleep(0.5)
            ui.update_memory("important", transcript)
        elif "todo" in transcript.lower():
            await asyncio.sleep(0.5)
            ui.update_memory("todo", transcript)
        elif "contact" in transcript.lower():
            await asyncio.sleep(0.5)
            ui.update_memory("contact", transcript)
    
    print("✅ Demo completed! Close the window to exit.")
    
    # Keep running until window is closed
    while ui.is_running():
        await asyncio.sleep(1)
    
    print("👋 UI window closed. Demo finished.")

if __name__ == "__main__":
    print("🎧 Omi Transcript UI Demo")
    print("=" * 40)
    print("This demo shows how the real-time transcript window works.")
    print("Watch as sample transcripts appear and memories are created!")
    print("=" * 40)
    
    try:
        asyncio.run(demo_transcript_ui())
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
