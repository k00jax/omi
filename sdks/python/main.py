import asyncio
import os
import ctypes
import sys
from omi.bluetooth import listen_to_omi
from omi.transcribe import transcribe
from omi.decoder import OmiOpusDecoder
from asyncio import Queue
from memory import init_memory_storage, process_transcript_for_memory, cleanup_memory_storage
from env_config import setup_environment
from transcript_ui import TranscriptWindow

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

    # Initialize the transcript UI window
    print("🖥️ Starting transcript UI window...")
    ui = TranscriptWindow()
    ui.update_status("🔄 Initializing Omi connection...")

    # Initialize memory storage
    omi_api_key = os.getenv("OMI_API_KEY")
    if omi_api_key:
        print("🧠 Initializing memory storage with MCP...")
        ui.update_status("🧠 Initializing memory storage with MCP...")
        init_memory_storage(omi_api_key, user_id=os.getenv("OMI_USER_ID", "default_user"))
    else:
        print("⚠️  OMI_API_KEY not set. Memory storage will use local fallback only.")
        ui.update_status("⚠️ Using local memory storage...")
        init_memory_storage("dummy_key", user_id="default_user")  # Will fallback to local storage

    audio_queue = Queue()
    decoder = OmiOpusDecoder()

    def handle_ble_data(sender, data):
        decoded_pcm = decoder.decode_packet(data)
        if decoded_pcm:
            try:
                audio_queue.put_nowait(decoded_pcm)
                # Track audio activity (minimal logging)
                if hasattr(handle_ble_data, 'counter'):
                    handle_ble_data.counter += 1
                else:
                    handle_ble_data.counter = 1
                
                # Only log every 500th packet (much less verbose)
                if handle_ble_data.counter % 500 == 0:
                    print(f"🎤 Audio: {handle_ble_data.counter} packets processed")
            except Exception as e:
                print("Queue Error:", e)

    async def on_transcript(transcript):
        print("🎯 Caught transcript in handler:", transcript)
        
        # Update the UI window with new transcript
        ui.update_transcript(transcript)

        # Process transcript for hot phrases and commands
        print(f"🔍 Processing transcript: '{transcript}'")  # Debug output
        action_taken, result = await process_transcript_for_memory(transcript)
        print(f"🔍 Action taken: {action_taken}, Result: {result}")  # Debug output
        
        if action_taken and result:
            if result.startswith("command:"):
                # Command was executed
                print("🎯 Command executed successfully!")
                ui.update_status(f"✅ {result[8:]}")  # Remove "command: " prefix
            else:
                # Memory was created
                print("📌 Memory created successfully!")
                ui.update_memory(result, transcript)
    
    async def run():
        try:
            ui.update_status("🔵 Connecting to Omi device...")
            
            # Create tasks for the main operations
            omi_task = asyncio.create_task(listen_to_omi(OMI_MAC, OMI_CHAR_UUID, handle_ble_data, ui.update_status))
            transcribe_task = asyncio.create_task(transcribe(audio_queue, api_key, on_transcript, ui.update_status))
            
            # Monitor if UI window is closed
            async def monitor_ui():
                while ui.is_running():
                    await asyncio.sleep(0.5)
                print("🖥️ UI window closed, stopping...")
                omi_task.cancel()
                transcribe_task.cancel()
            
            ui_monitor = asyncio.create_task(monitor_ui())
            
            # Run all tasks concurrently
            await asyncio.gather(
                omi_task,
                transcribe_task,
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

    asyncio.run(run())

if __name__ == '__main__':
    main()
