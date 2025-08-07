"""
Quick UI Test - Shows the transcript window with a simple test message
"""

from transcript_ui import TranscriptWindow
import time

print("🎧 Testing Transcript UI...")
print("This will open a window and add some test content.")

# Create the UI window
ui = TranscriptWindow("🧪 UI Test")

# Give it a moment to initialize
time.sleep(1)

# Add some test content
ui.update_status("🟢 UI Test Active")
ui.update_transcript("This is a test message!")
ui.update_transcript("The transcript window is working correctly.")
ui.update_memory("note", "This is a test memory")

print("✅ Test content added to window.")
print("🖥️ Check the transcript window - it should show test messages.")
print("💡 Close the window or press Ctrl+C to exit.")

try:
    # Keep running until window is closed
    while ui.is_running():
        time.sleep(1)
    print("👋 Window closed.")
except KeyboardInterrupt:
    print("\n🛑 Test interrupted.")

print("✅ UI test completed!")
