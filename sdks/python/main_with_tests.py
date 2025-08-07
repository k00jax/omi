#!/usr/bin/env python3
"""
Enhanced main.py that works with both real audio and includes transcript testing
This version will show you transcripts while we work on the Opus decoder
"""

import asyncio
import os
import sys
import ctypes
from transcript_ui import TranscriptWindow
from memory import init_memory_storage, process_transcript_for_memory, cleanup_memory_storage
from env_config import setup_environment
from omi.bluetooth import listen_to_omi
from omi.transcribe import transcribe
from omi.decoder import OmiOpusDecoder

# Configuration
OMI_CHAR_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"

# Force-load libopus from local directory if available
dll_path = os.path.join(os.path.dirname(__file__), "libopus-0.dll")
if os.path.exists(dll_path):
    ctypes.cdll.LoadLibrary(dll_path)
    print("✅ Loaded libopus-0.dll for optimal audio decoding")
else:
    print(f"⚠️  libopus-0.dll not found at: {dll_path}")
    print("🔄 Will use fallback decoder (limited functionality)")

def main():
    # Setup environment variables
    print("🔧 Setting up environment...")
    if not setup_environment():
        print("❌ Environment setup failed. Check your configuration.")
        return
    
    # Get OMI_MAC after environment is loaded
    OMI_MAC = os.getenv("OMI_MAC")
    if not OMI_MAC:
        print("❌ OMI_MAC is required but not set in .env file.")
        print("💡 Please add OMI_MAC=your_device_mac_address to your .env file")
        return

    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        print("❌ DEEPGRAM_API_KEY is required but not set.")
        print("💡 Create a .env file based on .env.example")
        return

    print(f"🎧 Using Omi device: {OMI_MAC}")

    # Initialize components
    print("🖥️ Starting transcript UI window...")
    ui = TranscriptWindow()
    ui.update_status("🔄 Initializing Omi connection...")

    # Initialize memory storage
    omi_key = os.getenv("OMI_API_KEY")
    user_id = os.getenv("USER_ID", "default_user")
    
    try:
        print("🧠 Initializing memory storage with MCP...")
        init_memory_storage(omi_key, user_id=user_id)
        ui.update_status("🧠 Memory storage initialized with MCP")
    except Exception as e:
        print(f"⚠️  MCP initialization failed: {e}")
        print("⚠️  Using local memory storage...")
        init_memory_storage("local_fallback", user_id=user_id)
        ui.update_status("⚠️  Using local memory storage...")

    # Audio processing components
    audio_queue = asyncio.Queue()
    decoder = OmiOpusDecoder()

    def handle_ble_data(sender, data):
        decoded_pcm = decoder.decode_packet(data)
        if decoded_pcm:
            try:
                audio_queue.put_nowait(decoded_pcm)
                # Only show audio activity occasionally to avoid spam
                if hasattr(handle_ble_data, 'counter'):
                    handle_ble_data.counter += 1
                else:
                    handle_ble_data.counter = 1
                
                if handle_ble_data.counter % 50 == 0:  # Show every 50th packet
                    non_zero_bytes = sum(1 for b in decoded_pcm if b != 0)
                    print(f"🎤 Audio flowing: packet #{handle_ble_data.counter}, {non_zero_bytes} non-zero bytes")
            except Exception as e:
                print("Queue Error:", e)

    async def on_transcript(transcript):
        print("🎯 Caught transcript in handler:", transcript)
        
        # Update the UI window with new transcript
        ui.update_transcript(transcript)

        # Process transcript for hot phrases and create memory
        memory_created, category = await process_transcript_for_memory(transcript)
        
        if memory_created and category:
            print("📌 Memory created successfully!")
            ui.update_memory(category, transcript)
    
    # Test transcript injection for demo purposes
    async def inject_test_transcripts():
        """Inject some test transcripts to show the system working while audio decoding is fixed"""
        test_phrases = [
            "Testing the transcript system",
            "Remember to check the audio decoder",
            "The system is processing audio data correctly",
            "Note that we need to fix the Opus decoder",
        ]
        
        await asyncio.sleep(10)  # Wait a bit for system to start
        
        for i, phrase in enumerate(test_phrases):
            if not ui.is_running():
                break
                
            await asyncio.sleep(15)  # Wait between test phrases
            print(f"🧪 Injecting test transcript {i+1}: {phrase}")
            await on_transcript(f"[TEST] {phrase}")
    
    async def run():
        try:
            ui.update_status("🔵 Connecting to Omi device...")
            
            # Create tasks for the main operations
            omi_task = asyncio.create_task(listen_to_omi(OMI_MAC, OMI_CHAR_UUID, handle_ble_data, ui.update_status))
            transcribe_task = asyncio.create_task(transcribe(audio_queue, api_key, on_transcript, ui.update_status))
            
            # Add test transcript injection
            test_task = asyncio.create_task(inject_test_transcripts())
            
            # Monitor if UI window is closed
            async def monitor_ui():
                while ui.is_running():
                    await asyncio.sleep(0.5)
                print("🖥️ UI window closed, stopping...")
                omi_task.cancel()
                transcribe_task.cancel()
                test_task.cancel()
            
            ui_monitor = asyncio.create_task(monitor_ui())
            
            # Run all tasks concurrently
            await asyncio.gather(
                omi_task,
                transcribe_task,
                test_task,
                ui_monitor,
                return_exceptions=True
            )
            
        except KeyboardInterrupt:
            print("🛑 Interrupted by user")
            ui.update_status("🛑 Stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
            ui.update_status(f"❌ Error: {e}")
        finally:
            # Cleanup resources
            print("🧹 Cleaning up...")
            ui.update_status("🧹 Cleaning up...")
            await cleanup_memory_storage()

    # Run the main loop
    asyncio.run(run())

if __name__ == "__main__":
    main()
