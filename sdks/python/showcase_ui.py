"""
Simple UI showcase - shows the transcript window working
Run this to see the UI in action without any async complexity
"""

from transcript_ui import TranscriptWindow
import time
import threading

def add_sample_content(ui):
    """Add sample content to demonstrate the UI"""
    time.sleep(2)  # Wait for UI to initialize
    
    ui.update_status("🟢 Demo Active")
    time.sleep(1)
    
    # Add some sample transcripts
    ui.update_transcript("Welcome to the Omi Python SDK!")
    time.sleep(2)
    
    ui.update_transcript("This is a real-time transcript demonstration.")
    time.sleep(2)
    
    ui.update_transcript("Note this: The UI window shows live transcriptions.")
    ui.update_memory("note", "The UI window shows live transcriptions.")
    time.sleep(3)
    
    ui.update_transcript("I have an idea for improving the interface.")
    ui.update_memory("idea", "I have an idea for improving the interface.")
    time.sleep(2)
    
    ui.update_transcript("This is important: The system works perfectly!")
    ui.update_memory("important", "This is important: The system works perfectly!")
    time.sleep(2)
    
    ui.update_transcript("The demo is now complete.")
    ui.update_status("✅ Demo Complete - Close window to exit")

def main():
    print("🎧 Omi Transcript UI Showcase")
    print("=" * 50)
    print("Opening the transcript window...")
    print("Watch as sample content is added automatically!")
    print("Close the window when you're done exploring.")
    print("=" * 50)
    
    # Create the UI
    ui = TranscriptWindow("🎧 Omi Transcript Showcase")
    
    # Start a thread to add sample content
    content_thread = threading.Thread(target=add_sample_content, args=(ui,), daemon=True)
    content_thread.start()
    
    print("✅ Transcript window opened!")
    print("💡 Try the controls:")
    print("   • A+/A- buttons to change font size")
    print("   • Clear button to reset content") 
    print("   • Save button to export transcript")
    print("\n🖱️ Close the window to exit...")
    
    # Wait for the UI to close
    try:
        while ui.is_running():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    
    print("👋 Transcript window closed. Showcase complete!")

if __name__ == "__main__":
    main()
